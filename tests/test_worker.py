# -*- coding: utf-8 -*-
"""
Tests for apns_proxy_server.worker
"""
from binascii import b2a_hex
import mock
from Queue import Queue

from nose.tools import ok_, eq_, raises
from apns import Frame, PayloadTooLargeError

from apns_proxy_server.worker import SendWorkerThread

dummy_setting = {
    'task_queue': Queue(),
    'name': 'test_thread',
    'use_sandbox': True,
    'cert_file': 'dummy.cert',
    'key_file': 'dummy.key'
}

dummy_token = '09ac5fe24292a611631994d5abb308e0e939a6551294c8b323337ca45f9ced06'


def test_create_instance():
    ok_(SendWorkerThread(**dummy_setting))


def test_add_frame():
    worker = SendWorkerThread(**dummy_setting)
    frame = Frame()
    ok_(len(frame.frame_data) == 0)
    worker._add_frame_item(frame, dummy_token, 1, expiry=None, priority=10, alert='Hello')

    hex_frame = b2a_hex(frame.frame_data)
    # Notification command
    eq_('02', hex_frame[0:2])
    # Frame length
    eq_('00000051', hex_frame[2:10])
    # Item ID:1 Device Token
    eq_('01', hex_frame[10:12])
    # Token Length
    eq_('0020', hex_frame[12:16])
    # Token
    eq_(dummy_token, hex_frame[16:80])


def test_create_frame_with_full_args():
    worker = SendWorkerThread(**dummy_setting)
    frame = Frame()
    worker._add_frame_item(frame, dummy_token, 1,
                           expiry=None,
                           priority=10,
                           alert='Hello',
                           sound='default',
                           badge=99,
                           custom={
                               'foo': 'bar'
                           },
                           content_available=True)
    ok_(len(frame.frame_data) > 0)


@raises(PayloadTooLargeError)
def test_create_frame_with_too_large_content():
    worker = SendWorkerThread(**dummy_setting)
    frame = Frame()
    worker._add_frame_item(frame, dummy_token, 1, expiry=None, priority=10,
                           alert='This is too large messageeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
                           sound='default',
                           badge=99,
                           custom={
                               'foo': 'foooooooooooooooooooooooooooooooooooooooooooooooo',
                               'bar': 'barrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr',
                               'buz': 'buzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
                           },
                           content_available=True)


def test_send():
    """
    send method should called
    """
    q = Queue()
    worker = SendWorkerThread(**{
        'task_queue': q,
        'name': 'test_thread',
        'use_sandbox': True,
        'cert_file': 'dummy.cert',
        'key_file': 'dummy.key'
    })
    worker.send = mock.Mock()
    worker.check_error = mock.Mock()
    q.put({
        'appid': 'unittest',
        'token': dummy_token,
        'aps': {
            'alert': 'Hello',
            'sound': 'default'
        }
    })
    worker.main()
    eq_(True, worker.send.called)
    eq_(True, worker.check_error.called)


def test_send_with_test():
    """
    When all messages are test=True, send method never called
    """
    q = Queue()
    worker = SendWorkerThread(**{
        'task_queue': q,
        'name': 'test_thread',
        'use_sandbox': True,
        'cert_file': 'dummy.cert',
        'key_file': 'dummy.key'
    })
    worker.send = mock.Mock()
    worker.check_error = mock.Mock()
    q.put({
        'appid': 'unittest',
        'token': dummy_token,
        'aps': {
            'alert': 'Hello',
            'sound': 'default'
        },
        'test': True
    })
    worker.main()
    eq_(False, worker.send.called)
    eq_(False, worker.check_error.called)
