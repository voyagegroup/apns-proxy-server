# -*- coding: utf-8 -*-

import logging
import socket
import time
import threading
from binascii import b2a_hex
from struct import unpack

from apns import APNs, Payload, Frame


class APNsError(Exception):
    def __init__(self, status_code, token_idx):
        self.status_code = status_code
        self.token_idx = token_idx
        self.msg = 'Invalid token found. Status: %s' % status_code

    def __str__(self):
        return self.msg


class SendWorkerThread(threading.Thread):
    """
    APNs送信用のワーカースレッド
    """
    def __init__(self, queue, name, use_sandbox, cert_file, key_file):
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.queue = queue
        self.name = name

        self.use_sandbox = use_sandbox
        self.cert_file = cert_file
        self.key_file = key_file
        self._apns = None

        self.count = 0
        # どのトークンがエラーになったか後で確認するための辞書
        self.recent_sended = {}
        # 定期的にエラーレスポンスをチェックするためのタイムスタンプ
        self.last_error_checked_time = time.time()
        # 一定時間送信しない場合は、APNsサーバーとの接続を切るためのタイムスタンプ
        self.last_sended_time = time.time()

    @property
    def apns(self):
        if self._apns is None:
            logging.info('Get APNs Instance')
            logging.info(self.cert_file)
            logging.info(self.key_file)
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
            item = self.queue.get()
            logging.debug("%s %s" % (self.name, item))
            self.count += 1
            self.recent_sended[self.count] = item['token']
            self.send(item['token'], item.get('aps'), item.get('test'))
            self.error_check()

    def send(self, token, aps, test=False):
        if test is True:
            return
        self.apns.gateway_server.send_notification_multiple(
            self.create_frame(token, self.count, **aps)
        )

    def create_frame(self, token, identifier, alert, sound, badge, expiry):
        payload = Payload(alert=alert, sound=sound, badge=badge)
        priority = 10
        if expiry is None:
            expiry = int(time.time()) + (60 * 60)  # 1 hour
        frame = Frame()
        frame.add_item(token, payload, identifier, expiry, priority)
        return frame

    def error_check(self):
        now_time = time.time()
        if (self.count % 500 == 0) or (now_time - self.last_error_checked_time > 2):
            try:
                logging.info('%s Check error response %i' % (self.name, self.count))
                self.check_apns_error_response()
            except APNsError, ape:
                # 不正なトークン、APNsからは接続が切られるので、再接続して続行する
                logging.warn(ape.msg)
                logging.warn("Invalid token found %s", self.recent_sended[ape.token_idx])
                self.clear_connection()
            except socket.error, e:
                if isinstance(e.args, tuple):
                    logging.warn("errno is %s" % str(e[0]))
                logging.warn(e)
                self.clear_connection()
            finally:
                self.recent_sended = {}
                self.last_error_checked_time = time.time()

    def check_apns_error_response(self):
        """
        APNsのエラーレスポンスをチェックする
        エラーが無い時はタイムアウトする
        """
        if self.apns.gateway_server._socket is None:
            logging.warn("Connection has not established")
            return

        try:
            self.apns.gateway_server._socket.settimeout(0.5)
            error_bytes = self.apns.gateway_server.read(6)

            if len(error_bytes) < 6:
                return

            # エラー有り
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
