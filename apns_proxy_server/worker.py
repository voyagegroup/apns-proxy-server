# -*- coding: utf-8 -*-

import logging
import Queue
import socket
import ssl
import time
import threading
import traceback
from binascii import b2a_hex
from struct import unpack

from apns import APNs, Payload, PayloadAlert, Frame, PayloadTooLargeError


class APNsError(Exception):
    """
    Representation of error from APNs error response.
    --------------------------
    Status Code
    --------------------------
      0 No errors encountered
      1 Processing error
      2 Missing device token
      3 Missing topic
      4 Missing payload
      5 Invalid token size
      6 Invalid topic size
      7 Invalid payload size
      8 Invalid token
     10 Shutdown
    255 None (unknown)
    --------------------------
    @see https://developer.apple.com/jp/devcenter/ios/library/documentation/RemoteNotificationsPG.pdf
    """
    def __init__(self, status_code, token_idx):
        self.status_code = status_code
        self.token_idx = token_idx
        self.msg = 'Invalid frame found. Status: %s' % status_code

    def __str__(self):
        return self.msg


class QueueWaitTimeout(Exception):
    pass


class SendWorkerThread(threading.Thread):
    """
    Worker thread
    """

    # Number of to keep sended item
    # It is necessary to hold for a while after sending to retry.
    # Because error response will become asynchronously
    KEEP_SENDED_ITEMS_NUM = 2000

    # Task queue timeout to clear connection (sec)
    TASK_QUEUE_TIMEOUT = 5 * 60  # 5min

    def __init__(self, task_queue, name, use_sandbox, cert_file, key_file):
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.task_queue = task_queue
        self.name = name

        self.use_sandbox = use_sandbox
        self.cert_file = cert_file
        self.key_file = key_file
        self._apns = None

        self.count = 0
        self.recent_sended = {}

    @property
    def apns(self):
        if self._apns is None:
            self._apns = APNs(
                use_sandbox=self.use_sandbox,
                cert_file=self.cert_file,
                key_file=self.key_file
            )
        return self._apns

    def clear_connection(self):
        self._apns = None

    def run(self):
        while True:
            try:
                while True:
                    self.main()
            except QueueWaitTimeout:
                pass
            except ssl.SSLError, ssle:
                # Invalid pem file. Kill this thread
                logging.error(ssle)
                raise ssle
            except socket.error, e:
                logging.warn(e)
                logging.warn(traceback.format_exc())
                # Some errors
                # (1) Connection lost by sending invalid token
                #     Disconnect from remote server before self.check_error() called.
                # (2) Connection lost by too long connection
                # We cannot know which item was invalid. So retry last one.
                self.retry_last_one()
            finally:
                self.clear_connection()

    def main(self):
        frame = Frame()
        try:
            item_count = 0
            while item_count < 500:
                if item_count == 0:
                    # First time
                    # Wait here by blocking get
                    item = self.task_queue.get(True, self.TASK_QUEUE_TIMEOUT)
                else:
                    item = self.task_queue.get(False)
                item_count += 1

                self.count += 1
                self.store_item(self.count, item)
                self.add_frame_item(frame, **item)
        except Queue.Empty:
            if item_count == 0:
                raise QueueWaitTimeout()

        if len(frame.frame_data) > 0:
            self.send(frame)
            self.check_error()

    def add_frame_item(self, frame, appid, token, aps, expiry=None, priority=10, test=False):
        if test is True:
            return

        try:
            logging.debug('Add to frame %s' % token)
            logging.debug(aps)
            self._add_frame_item(frame, token, self.count, expiry, priority, **aps)
        except PayloadTooLargeError, pe:
            logging.warn('Too large payload, size:%d. %s' % (pe.payload_size, aps))

    def _add_frame_item(self, frame, token, identifier, expiry, priority,
                        alert=None, sound=None, badge=None, custom={}, content_available=False):
        if isinstance(alert, dict):
            alert = PayloadAlert(**alert)
        payload = Payload(alert=alert,
                          sound=sound,
                          badge=badge,
                          custom=custom,
                          content_available=content_available)

        if expiry is None:
            expiry = int(time.time()) + (60 * 60)  # 1 hour
        frame.add_item(token, payload, identifier, expiry, priority)

    def send(self, frame):
        self.apns.gateway_server.send_notification_multiple(frame)

    def store_item(self, idx, item):
        self.recent_sended[idx] = item
        if idx > self.KEEP_SENDED_ITEMS_NUM:
            self.recent_sended.pop(idx - self.KEEP_SENDED_ITEMS_NUM)

    def retry_last_one(self):
        self.retry_from(self.count)

    def retry_from(self, start_token_idx):
        """
        Retry items.
        Add task queue from stored item.
        """
        idx = start_token_idx
        while idx <= self.count:
            self.task_queue.put(self.recent_sended[idx])
            idx += 1

    def check_error(self):
        try:
            logging.info('%s Check error response %i' % (self.name, self.count))
            self.check_apns_error_response()
        except APNsError, ape:
            logging.warn(ape.msg)
            # Error response found. Current connection will lost.
            self.clear_connection()
            if ape.token_idx in self.recent_sended:
                # Retry items after invalid frame
                logging.warn("Invalid token found %s", self.recent_sended[ape.token_idx]['token'])
                self.retry_from(ape.token_idx + 1)
            else:
                # Cannot retry
                pass

    def check_apns_error_response(self):
        """
        Check error response.
        Use blocking socket.read() and timeout when no response.

        This is experimentally workaround.
        """
        if self.apns.gateway_server._socket is None:
            return

        try:
            self.apns.gateway_server._socket.settimeout(0.6)
            error_bytes = self.apns.gateway_server.read(6)
            if len(error_bytes) < 6:
                return

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
