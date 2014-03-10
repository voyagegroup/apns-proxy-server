# -*- coding: utf-8 -*-

import logging
from Queue import Queue
import traceback

import simplejson as json
import zmq

from . import worker

COMMAND_LENGTH = 1
COMMAND_ASK_ADDRESS = b'\1'
COMMAND_SEND = b'\2'


class APNSProxyServer(object):
    """
    APNs Proxy Server

    サーバーは2つのポートを利用する。

    1. ZMQ REQ-REP Connection
    REQ-REP接続は、応答が必要な処理に利用する。これは同期処理になる。

    2. ZMQ PUSH-PULL Connection
    PUSH-PULL接続は、ストリーム処理に利用する。サーバーは応答を返さない。
    Push通知の内容はPULL Socketで受ける。
    """

    def __init__(self, settings):
        self.settings = settings
        self.task_queues = {}

    def start(self):
        logging.info('Start server.')
        self.create_workers(
            self.settings.APPLICATIONS,
            self.settings.THREAD_NUMS_PER_APPLICATION
        )

        logging.info('Use port %s' % self.settings.BIND_PORT_FOR_ENTRY)
        logging.info('Use port %s' % self.settings.BIND_PORT_FOR_PULL)

        context = zmq.Context()
        rep_server = context.socket(zmq.REP)
        rep_server.bind("tcp://*:" + str(self.settings.BIND_PORT_FOR_ENTRY))

        pull_server = context.socket(zmq.PULL)
        pull_server.bind("tcp://*:" + str(self.settings.BIND_PORT_FOR_PULL))

        poller = zmq.Poller()
        poller.register(rep_server, zmq.POLLIN)
        poller.register(pull_server, zmq.POLLIN)

        try:
            while 1:
                items = dict(poller.poll())
                if pull_server in items:
                    # PULL socket cannot return
                    self.process_message(pull_server.recv())
                if rep_server in items:
                    # REP socket must return
                    result = self.process_message(rep_server.recv())
                    rep_server.send(result)
        except Exception, e:
            logging.error(e)
            logging.error(traceback.format_exc())
        finally:
            rep_server.close()
            pull_server.close()
            context.term()

    def process_message(self, message):
        command = message[:1]
        if command == COMMAND_ASK_ADDRESS:
            return str(self.settings.BIND_PORT_FOR_PULL)
        elif command == COMMAND_SEND:
            self.dispatch_queue(message[1:])
        else:
            logging.warn('Unknown command received %s' % command)

    def dispatch_queue(self, message):
        """
        ワーカーにデータを渡す
        """
        data = self.parse_message(message)
        application_id = data.get('appid')
        if application_id in self.task_queues:
            self.task_queues[application_id].put(data)
            return True
        else:
            logging.warn('Unknown application_id received %s' % application_id)
            return False

    def parse_message(self, message):
        """
        データフレームから各値を取り出す
        """
        return json.loads(message)

    def create_workers(self, applications, nums_per_apps):
        """
        ワーカースレッドと、ワーカーとやりとりをするタスクキューの生成
        """
        for app in applications:
            task_queue = Queue()
            for i in xrange(nums_per_apps):
                self.create_worker(app, task_queue, i)
            self.task_queues[app['application_id']] = task_queue

    def create_worker(self, app_config, task_queue, sub_no):
        """
        スレッドの生成
        """
        thread_name = "SendWorker:%s_%i" % (app_config['name'], sub_no)
        thread = worker.SendWorkerThread(
            task_queue,
            thread_name,
            app_config['sandbox'],
            app_config['cert_file'],
            app_config['key_file']
        )
        thread.start()
        logging.info('Thread created %s' % thread_name)
