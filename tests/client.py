# -*- coding: utf-8 -*-
"""
APNS Proxy Serverのクライアント

Usage:
    client = APNSProxyClient("tcp://localhost:5556", "01")
    with client:
        token = "xxae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec1"
        msg = u"これはメッセージAです"
        client.send(token, msg)

        token = "xxae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec2"
        msg = u"これはメッセージBです"
        client.send(token, msg)
"""

import zmq
import simplejson as json


PING_TIMEOUT = 1500  # msec
RECV_TIMEOUT = 9000  # msec

COMMAND_PING = b'1'
COMMAND_TOKEN = b'2'
COMMAND_FLUSH = b'z'

DEVICE_TOKEN_LENGTH = 64
MAX_MESSAGE_LENGTH = 255


class APNSProxyClient(object):

    def __init__(self, address, application_id):
        """ZMQコンテキストとソケットの初期化"""
        if address is None:
            raise ValueError("address must be string")
        self.address = address

        self.context = zmq.Context()
        self.context.setsockopt(zmq.LINGER, 2000)

        self.client = self.context.socket(zmq.REQ)

        if not isinstance(application_id, str) or len(application_id) != 2:
            raise ValueError("application_id must be 2 length string")
        self.application_id = application_id

    def __enter__(self):
        """リモートサーバーへ接続"""
        self.client.connect(self.address)
        self.ping()

    def ping(self):
        self.client.send(COMMAND_PING)
        poller = zmq.Poller()
        poller.register(self.client, zmq.POLLIN)
        if poller.poll(PING_TIMEOUT):
            ret = self.client.recv()
            if ret != "OK":
                raise IOError("Invalid server state %s" % ret)
        else:
            self.close()
            raise IOError("Cannot connect to APNs Proxy Server. Timeout!!")

    def send(self, token, alert, sound='default', badge=None, expiry=None, test=False):
        """
        デバイストークンの送信
        """
        self._check_token(token)
        self._check_alert(alert)
        self.client.send(self._serialize(
            token, alert, sound, badge, expiry, test
        ), zmq.SNDMORE)
        self.flush()

    def send_more(self, token, alert, sound='default', badge=None, expiry=None, test=False):
        """
        デバイストークンの送信
        """
        self._check_token(token)
        self._check_alert(alert)
        self.client.send(self._serialize(
            token, alert, sound, badge, expiry, test
        ), zmq.SNDMORE)

    @staticmethod
    def _check_token(token):
        if len(token) != DEVICE_TOKEN_LENGTH:
            raise ValueError('Invalid token length %s' % token)

    @staticmethod
    def _check_alert(alert):
        if len(alert) > MAX_MESSAGE_LENGTH:
            raise ValueError('Too long message')

    def _serialize(self, token, alert, sound, badge, expiry, test):
        """
        送信データのフォーマット
        """
        return COMMAND_TOKEN + json.dumps({
            'appid': self.application_id,
            'token': token,
            'test': 'test' if test else '',
            'aps': {
                'alert': alert,
                'sound': sound,
                'badge': badge,
                'expiry': expiry
            }
        }, ensure_ascii=True)

    def flush(self):
        self.client.send(COMMAND_FLUSH)
        poller = zmq.Poller()
        poller.register(self.client, zmq.POLLIN)
        if poller.poll(RECV_TIMEOUT):
            self.client.recv()
        else:
            self.close()
            raise IOError("Server cannot respond. Some messages may lost.")

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.close()
            return False
        # バッファに残っているメッセージを確実に流しきる
        self.flush()
        return True

    def close(self):
        self.client.close()
        self.context.term()
