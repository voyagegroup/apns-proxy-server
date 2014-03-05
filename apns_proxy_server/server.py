# -*- coding: utf-8 -*-
"""
APNs Proxy Server

サーバーは2つのポートを利用する。

1. ZMQ REQ-REP Connection
REQ-REP接続は、応答が必要な処理に利用する。これは同期処理になる。

2. ZMQ PUSH-PULL Connection
PUSH-PULL接続は、ストリーム処理に利用する。サーバーは応答を返さない。
Push通知の内容はPULL Socketで受ける。
"""

import logging
from Queue import Queue
import traceback

import simplejson as json
import zmq

import settings
from . import worker

COMMAND_LENGTH = 1
COMMAND_ASK_ADDRESS = b'1'

task_queues = {}


def start():
    logging.info('Start server.')
    logging.info('Use port %s' % settings.BIND_PORT_FOR_ENTRY)
    logging.info('Use port %s' % settings.BIND_PORT_FOR_PULL)

    context = zmq.Context()
    rep_server = context.socket(zmq.REP)
    rep_server.bind("tcp://*:" + str(settings.BIND_PORT_FOR_ENTRY))

    pull_server = context.socket(zmq.PULL)
    pull_server.bind("tcp://*:" + str(settings.BIND_PORT_FOR_PULL))

    poller = zmq.Poller()
    poller.register(rep_server, zmq.POLLIN)
    poller.register(pull_server, zmq.POLLIN)

    try:
        while 1:
            items = dict(poller.poll())
            if pull_server in items:
                dispatch(pull_server.recv())
            if rep_server in items:
                # Now ping message only
                rep_server.recv()
                rep_server.send(str(settings.BIND_PORT_FOR_PULL))
    except Exception, e:
        logging.error(e)
        logging.error(traceback.format_exc())
    finally:
        rep_server.close()
        pull_server.close()
        context.term()


def dispatch(message):
    """
    ワーカーにメッセージを渡す
    """
    data = parse_message(message)
    application_id = data.get('appid')
    if not application_id in task_queues:
        try:
            q = Queue()
            create_worker(application_id, q)
            task_queues[application_id] = q
        except ValueError, ve:
            logging.error(ve)
            return
    task_queues[application_id].put(data)


def parse_message(message):
    """
    データフレームから各値を取り出す
    """
    return json.loads(message)


def create_worker(application_id, task_queue):
    logging.info("Create worker for: %s" % application_id)
    app_config = get_application_config(application_id)
    for i in xrange(settings.THREAD_NUMS_PER_APPLICATION):
        thread_name = "SendWorker:%s_%i" % (app_config['name'], i)
        thread = worker.SendWorkerThread(
            task_queue,
            thread_name,
            app_config['sandbox'],
            app_config['cert_file'],
            app_config['key_file']
        )
        thread.start()


def get_application_config(application_id):
    for c in settings.APPLICATIONS:
        if c['application_id'] == application_id:
            return c
    raise ValueError('Unknown application_id given. (%s)' % application_id)
