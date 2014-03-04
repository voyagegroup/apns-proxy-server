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
COMMAND_PING = b'1'
COMMAND_TOKEN = b'2'
COMMAND_FLUSH = b'z'

task_queues = {}


def start(address):
    context = zmq.Context()
    server = context.socket(zmq.REP)
    server.bind(address)
    try:
        while 1:
            message = server.recv()
            logging.debug("Received %s" % message)
            command = message[:COMMAND_LENGTH]
            if command == COMMAND_TOKEN:
                dispatch(message)
            elif command == COMMAND_PING:
                reply(server)
            elif command == COMMAND_FLUSH:
                reply(server)
            else:
                logging.warn("UNKNOWN COMMAND Received:%s" % command)
    except Exception, e:
        logging.error(e)
        logging.error(traceback.format_exc())
    finally:
        server.close()
        context.term()


def reply(sock):
    sock.send(b"OK")


def parse_message(message):
    """
    データフレームから各値を取り出す
    """
    return json.loads(message[COMMAND_LENGTH:])


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
