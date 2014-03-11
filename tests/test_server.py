# -*- coding: utf-8 -*-
"""
serverモジュールのテスト
"""

import json
import threading
from Queue import Queue, Empty

from nose.tools import ok_, eq_, raises

from apns_proxy_server.server import (
    COMMAND_ASK_ADDRESS,
    COMMAND_SEND,
    APNSProxyServer)


def test_instance():
    import tests.data.valid_settings
    server = APNSProxyServer(tests.data.valid_settings)
    ok_(server)
    ok_(server.start)


def test_create_worker():
    server = APNSProxyServer({})
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
    server = APNSProxyServer({})
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
        "aps": {
            "alert": "This is test",
            "badge": 1,
            "sound": "default",
            "expiry": None
        }
    })), True, "Dispatch should be success")


def test_dispatch_unknown_app():
    server = APNSProxyServer({})
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

    server = APNSProxyServer({})
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
            server = APNSProxyServer(tests.data.valid_settings)
            server.start()
        except Exception, e:
            error_queue.put(e)

    q = Queue()
    thread = threading.Thread(target=server,args=(q,))
    thread.setDaemon(True)
    thread.start()

    try:
        error = q.get(True, 1)
        raise error
    except Empty:
        ok_(True)
