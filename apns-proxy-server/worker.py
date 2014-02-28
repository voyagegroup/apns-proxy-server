# -*- coding: utf-8 -*-

import errno
import logging
import socket
import time
import threading
from binascii import b2a_hex
from struct import unpack

from apns import APNs, Payload, Frame

def send_worker(queue, application_id, use_sandbox, cert_file, key_file):
    thread_name = threading.current_thread().name
    apns = get_apns_instance(use_sandbox, cert_file, key_file)
    while True:
        item = queue.get()
        logging.info("%s %s %s" % (thread_name, item.get('message'), item.get('token')))

def get_apns_instance(use_sandbox, cart_file, key_file):
    return APNs(
        use_sandbox=use_sandbox,
        cert_file=cert_file,
        key_file=key_file
    )
