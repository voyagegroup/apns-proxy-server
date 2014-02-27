# -*- coding: utf-8 -*-
"""
APNs Proxy Server

メッセージングにはZeroMQを使っている、メッセージフレームの構造は次の通り
------------------------------------------------------------------
| Command(1) | Application ID(2) | Device Token(64) | Message(n) |
------------------------------------------------------------------
括弧内は長さ
"""

import logging
import traceback
import threading
from Queue import Queue

import zmq


COMMAND_LENGTH = 1
APPLICATION_ID_LENGTH = 2
DEVICE_TOKEN_LENGTH = 64

COMMAND_PING = b'1'
COMMAND_TOKEN = b'2'
COMMAND_END = b'3'


def start(address):
    context = zmq.Context()
    server = context.socket(zmq.REP)
    server.bind(address)
    try:
        while 1:
            message = server.recv()
            command = message[:COMMAND_LENGTH]
            if command == COMMAND_TOKEN:
                dispatch(message)
            elif command == COMMAND_PING:
                logging.debug("Ping command received")
                server.send("OK")
            elif command == COMMAND_END:
                logging.debug("END command received")
                server.send("OK")
            else:
                logging.warn("UNKNOWN COMMAND Received:%s" % command)
    except Exception, e:
        logging.error(e)
        logging.error(traceback.format_exc())
    finally:
        server.close()
        context.term()


def parse_message(message):
    pos = COMMAND_LENGTH
    application_id = message[pos:pos+APPLICATION_ID_LENGTH]

    pos += APPLICATION_ID_LENGTH
    token = message[pos:pos+DEVICE_TOKEN_LENGTH]

    pos += DEVICE_TOKEN_LENGTH
    message = message[pos:]
    return (application_id, token, message)


task_queues = {}


def dispatch(message):
    application_id, token, message = parse_message(message)
#    logging.info("application_id: %s" % application_id)
#    logging.info("token: %s" % token)
#    logging.info("message: %s" % message)
    if not application_id in task_queues:
        thread, q = create_worker(application_id)
        thread.start()
        task_queues[application_id] = q

    task_queues[application_id].put({
        "message": message,
        "token": token
    })


def create_worker(application_id):
    logging.info("Create worker for: %s" % application_id)
    q = Queue()
    thread = threading.Thread(target=worker, args=(
        q,
        application_id
    ))
    return (thread, q)


def worker(queue, application_id):
    while True:
        item = queue.get()
        logging.info(application_id)
        logging.info(item.get('message'))
        logging.info(item.get('token'))

