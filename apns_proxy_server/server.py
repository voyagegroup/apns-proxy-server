# -*- coding: utf-8 -*-
"""
APNs Proxy Server
"""

import logging
import traceback
import threading
from Queue import Queue

import zmq
import simplejson as json

import settings
from . import worker

COMMAND_LENGTH = 1
COMMAND_ASK_ADDRESS = b'1'

task_queues = {}


def start(rep_port, pull_port):
    """
    サーバーの起動
    サーバーは2つのポートを利用する。

    1. ZMQ REQ-REP Connection
    REQ-REP接続は、応答が必要な処理に利用する。これは同期処理になる。

    2. ZMQ PUSH-PULL Socket
    PUSH-PULL接続は、ストリーム処理に利用する。サーバーは応答を返さない。
    Push通知の内容はPULL Socketで受ける。
    """
    context = zmq.Context()
    rep_server = context.socket(zmq.REP)
    rep_server.bind("tcp://*:" + str(rep_port))

    pull_server = context.socket(zmq.PULL)
    pull_server.bind("tcp://*:" + str(pull_port))

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
                rep_server.send(str(pull_port))
    except Exception, e:
        logging.error(e)
        logging.error(traceback.format_exc())
    finally:
        rep_server.close()
        pull_server.close()
        context.term()


def dispatch(message):
    """
    ワーカースレッドにメッセージを渡す
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

    #logging.debug("Dispatch to worker for application_id: %s" % application_id)
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
        thread = threading.Thread(target=worker.send_worker, name=thread_name, args=(
            task_queue,
            application_id,
            app_config['sandbox'],
            app_config['cert_file'],
            app_config['key_file']
        ))
        thread.start()


def get_application_config(application_id):
    for c in settings.APPLICATIONS:
        if c['application_id'] == application_id:
            return c
    raise ValueError('Unknown application_id given. (%s)' % application_id)
