# -*- coding: utf-8 -*-
"""
serverモジュールのテスト
"""

import json
import socket
import threading
from Queue import Queue, Empty

from nose.tools import ok_, eq_

from apns_proxy_server.server import (
    APNSProxyServer)
from apns_proxy_server import validator


dummy_setting = {
    'BIND_PORT_FOR_ENTRY': 1000,
    'BIND_PORT_FOR_PULL': 200,
    'THREAD_NUMS_PER_APPLICATION': 1,
    'APPLICATIONS': []
}


def test_instance():
    server = APNSProxyServer(dummy_setting)
    ok_(server)
    ok_(server.start)


def test_create_worker():
    server = APNSProxyServer(dummy_setting)
    server.create_workers([{
        "application_id": "myApp1",
        "name": "My App1",
        "sandbox": False,
        "cert_file": "sample.cert",
        "key_file": "sample.key"
    }, {
        "application_id": "myApp2",
        "name": "My App2",
        "sandbox": False,
        "cert_file": "sample.cert",
        "key_file": "sample.key"
    }], 1)
    eq_(len(server.task_queues), 2)
    for k in server.task_queues.keys():
        ok_(isinstance(server.task_queues[k], Queue))


def test_dispatch_known_app():
    server = APNSProxyServer(dummy_setting)
    server.create_workers([{
        "application_id": "myApp1",
        "name": "My App1",
        "sandbox": False,
        "cert_file": "sample.cert",
        "key_file": "sample.key"
    }, {
        "application_id": "myApp2",
        "name": "My App2",
        "sandbox": False,
        "cert_file": "sample.cert",
        "key_file": "sample.key"
    }], 1)

    token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    eq_(server.dispatch_queue(json.dumps({
        "token": token,
        "appid": "myApp1",
        "test": True,
        "aps": {
            "alert": "This is test",
            "badge": 1,
            "sound": "default",
            "expiry": None
        }
        })), True, "Dispatch should be success")

    eq_(server.dispatch_queue(json.dumps({
        "token": token,
        "appid": "myApp2",
        "test": True,
        "aps": {
            "alert": "This is test",
            "badge": 1,
            "sound": "default",
            "expiry": None
        }
        })), True, "Dispatch should be success")


def test_dispatch_unknown_app():
    server = APNSProxyServer(dummy_setting)
    server.create_workers([{
        "application_id": "myApp2",
        "name": "My App2",
        "sandbox": False,
        "cert_file": "sample.cert",
        "key_file": "sample.key"
    }], 1)

    token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    eq_(server.dispatch_queue(json.dumps({
        "token": token,
        "appid": "unknownApp",
        "test": True,
        "aps": {
            "alert": "This is test",
            "badge": 1,
            "sound": "default",
            "expiry": None
        }
        })), False, "Dispatch should be failed of unknown appid")


def test_thread_count():
    """
    スレッド生成数のテスト
    """
    before_num = threading.active_count()

    server = APNSProxyServer(dummy_setting)
    server.create_workers([{
        "application_id": "myApp1",
        "name": "My App1",
        "sandbox": False,
        "cert_file": "sample.cert",
        "key_file": "sample.key"
    }, {
        "application_id": "myApp2",
        "name": "My App2",
        "sandbox": False,
        "cert_file": "sample.cert",
        "key_file": "sample.key"
    }], 3)

    after_num = threading.active_count()

    eq_(before_num + 6, after_num)


def test_start():
    """
    サーバーが起動できる事のテスト
    """
    def server(error_queue):
        try:
            import tests.data.valid_settings
            s = validator.validate_settings(tests.data.valid_settings)
            server = APNSProxyServer(s)
            server.start()
        except Exception, e:
            error_queue.put(e)

    q = Queue()
    thread = threading.Thread(target=server, args=(q,))
    thread.setDaemon(True)
    thread.start()

    try:
        error = q.get(True, 1)
        raise error
    except Empty:
        ok_(True)


def test_connect():
    """
    待ちうけポートに接続できる事のテスト
    """
    def server():
        server = APNSProxyServer({
            'BIND_PORT_FOR_ENTRY': 15555,
            'BIND_PORT_FOR_PULL': 15556,
            'THREAD_NUMS_PER_APPLICATION': 5,
            'APPLICATIONS': []
        })
        server.start()

    thread = threading.Thread(target=server)
    thread.setDaemon(True)
    thread.start()

    socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket1.connect(('localhost', 15555))
    socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket2.connect(('localhost', 15556))

    ok_(True)
