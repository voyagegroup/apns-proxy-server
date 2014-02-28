# -*- coding: utf-8 -*-

import errno
import logging
import socket
import time
import threading
from binascii import b2a_hex
from struct import unpack

from apns import APNs, Payload, Frame


class APNsError(Exception):
    def __init__(self, status_code, token_idx, token):
        self.status_code = status_code
        self.token = token
        self.token_idx = token_idx
        self.msg = 'Invalid token found. Status: %s' % status_code

    def __str__(self):
        return self.msg


def send_worker(queue, application_id, use_sandbox, cert_file, key_file):
    """
    Method for send worker thread
    """
    thread_name = threading.current_thread().name

    recent_sended = {}
    counter = 0
    last_sended_time = time.time()

    while True:
        try:
            apns = get_apns_instance(use_sandbox, cert_file, key_file)
            while True:
                item = queue.get()
                logging.info("%s %s %s" % (thread_name, item.get('token'), item.get('aps')))
                counter += 1
                recent_sended[counter] = item.get('token')
                send(apns.gateway_server, create_frame(item.get('token'), counter, **item.get('aps')))

                cur_time = time.time()
                time_diff = cur_time - last_sended_time
                last_sended_time = cur_time
                if (counter % 500 == 0) or (time_diff > 1):
                    check_error_response(apns.gateway_server)
                    recent_sended = {}

        except APNsError, ape:
            # 不正なトークン、APNsからは接続が切られるので、再接続して続行する
            logging.warn(ape.msg)
            logging.warn("Invalid token found %s", recent_sended[ape.token_idx])
        except socket.error, e:
            if isinstance(e.args, tuple):
                logging.error("errno is %s" % str(e[0]))
                if e[0] == errno.EPIPE:
                    logging.warn("Connection disconnected")
                else:
                    logging.error(e)
            else:
                logging.error(e)


def send(server, frame):
    server.send_notification_multiple(frame)


def create_frame(token, identifier, message, sound, badge, expiry):
    payload = Payload(alert=message, sound=sound, badge=badge)
    priority = 10
    frame = Frame()
    frame.add_item(token, payload, identifier, expiry, priority)
    return frame


def check_error_response(server):
    """
    APNsのエラーレスポンスをチェックする
    エラーが無い時はタイムアウトする
    """
    if server._socket is None:
        logging.warn("Connection has not established")
        return

    try:
        server._socket.settimeout(0.5)
        error_bytes = server.read(6)

        if len(error_bytes) < 6:
            return

        logging.info("Error response %s" % b2a_hex(error_bytes))
        command = b2a_hex(unpack('>c', error_bytes[0:1])[0])
        if command != '08':
            logging.warn('Unknown command received %s', command)
            return

        status = b2a_hex(unpack('>c', error_bytes[1:2])[0])
        identifier = unpack('>I', error_bytes[2:6])[0]
        raise APNsError(status, identifier)

    except socket.error, e:
        if isinstance(e.args, tuple):
            if e[0] == 'The read operation timed out':
                return  # No error response.
        logging.warn(e)
    finally:
        server._socket.settimeout(1)


def get_apns_instance(use_sandbox, cert_file, key_file):
    logging.info('Get APNs Connection')
    logging.info(cert_file)
    logging.info(key_file)
    return APNs(
        use_sandbox=use_sandbox,
        cert_file=cert_file,
        key_file=key_file
    )
