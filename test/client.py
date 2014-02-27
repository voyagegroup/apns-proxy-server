# -*- coding: utf-8 -*-
"""
Usage:
client = APNSProxyClient("tcp://localhost:5556", "01")
with client:
    token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec1"
    msg = u"これはメッセージです"
    client.send(token, msg)

    ret = client.result()
"""

import zmq


COMMAND_PING = b'1'
COMMAND_TOKEN = b'2'
COMMAND_END = b'3'

DEVICE_TOKEN_LENGTH = 64
MAX_MESSAGE_LENGTH = 255


class APNSProxyClient(object):

    def __init__(self, address, application_id):
        """ZMQコンテキストとソケットの初期化"""
        if address is None:
            raise ValueError("address must be string")
        self.address = address

        self.context = zmq.Context()
        self.context.setsockopt(zmq.RCVTIMEO, 3000)
        self.context.setsockopt(zmq.SNDTIMEO, 3000)
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
        if poller.poll(2000):
            ret = self.client.recv()
            if ret != "OK":
                raise IOError("Invalid server state %s" % ret)
        else:
            self.close()
            raise IOError("Cannot connect to Server. Timeout!!")

    def send(self, token, message):
        """
        デバイストークンの送信
        """
        if len(token) != DEVICE_TOKEN_LENGTH:
            raise ValueError('Invalid token length %s' % token)
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError('Too long message')
        if isinstance(message, unicode):
            message = message.encode("utf-8")
        self.client.send(COMMAND_TOKEN + self.application_id + token + message, zmq.SNDMORE)

    def result(self):
        self.client.send(COMMAND_END)
        ret = self.client.recv()
        return ret

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.close()
            return False
        self.close()
        return True

    def close(self):
        self.client.close()
        self.context.term()
