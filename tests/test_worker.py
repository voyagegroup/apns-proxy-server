# -*- coding: utf-8 -*-
"""
Tests for apns_proxy_server.worker
"""
from binascii import b2a_hex
import mock
from Queue import Queue
import time

from nose.tools import ok_, eq_, raises
from apns import Frame, Payload, PayloadTooLargeError

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


def test_create_payload():
    worker = SendWorkerThread(**dummy_setting)
    payload = worker.create_payload(
        alert='Hello',
        content_available=True
    )
    ok_(isinstance(payload, Payload))


def test_create_payload_with_dict_alert():
    worker = SendWorkerThread(**dummy_setting)
    payload = worker.create_payload(
        alert={
            'body': 'Hello',
            'action_loc_key': 'loc_key'
        },
        content_available=True
    )
    ok_(isinstance(payload, Payload))


@raises(PayloadTooLargeError)
def test_create_payload_with_too_large_content():
    worker = SendWorkerThread(**dummy_setting)
    worker.create_payload(
        alert='This is too large messageeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
        sound='default',
        badge=999,
        custom={
            'foo': 'foooooooooooooooooooooooooooooooooooooooooooooooo',
            'bar': 'barrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr',
            'buz': 'buzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
        },
        content_available=True
    )


has_called_check_method = False


def test_add_frame_item():
    global has_called_check_method
    has_called_check_method = False

    # assert_called_once_with of Mock Class failes to compare Payload object.
    # So here created custom check method for parameter checking
    def check_add_item_args(token, payload, identifier, expiry, priority):
        default_expiry = int(time.time()) + (60 * 60)

        eq_(token, dummy_token)
        eq_(payload.alert, 'Hey')
        eq_(payload.badge, None)
        eq_(payload.sound, None)
        eq_(payload.custom, {})
        eq_(payload.content_available, False)
        eq_(identifier, 123)
        eq_(priority, 10, 'priority should set default value when skipped')
        eq_(expiry, default_expiry, 'expiry should set default value when skipped')

        global has_called_check_method
        has_called_check_method = True

    worker = SendWorkerThread(**dummy_setting)
    worker.count = 123
    frame = Frame()
    frame.add_item = check_add_item_args

    worker.add_frame_item(frame, 'myapp', dummy_token, {'alert': 'Hey'})
    ok_(has_called_check_method)


def test_add_frame_item_with_full_args():
    global has_called_check_method
    has_called_check_method = False

    # assert_called_once_with of Mock Class failes to compare Payload object.
    # So here created custom check method for parameter checking
    def check_add_item_args(token, payload, identifier, expiry, priority):
        eq_(token, dummy_token)
        eq_(payload.alert, 'Wow')
        eq_(payload.badge, 50)
        eq_(payload.sound, 'bell')
        eq_(payload.custom, {'foo': 'bar'})
        eq_(payload.content_available, True)
        eq_(identifier, 1)
        eq_(priority, 5)
        eq_(expiry, 0)

        global has_called_check_method
        has_called_check_method = True

    worker = SendWorkerThread(**dummy_setting)
    worker.count = 1
    frame = Frame()
    frame.add_item = check_add_item_args

    worker.add_frame_item(frame, 'myapp', dummy_token, {
        'alert': 'Wow',
        'badge': 50,
        'sound': 'bell',
        'custom': {'foo': 'bar'},
        'content_available': True,
    }, expiry=0, priority=5)
    ok_(has_called_check_method)


def test_frame_content():
    worker = SendWorkerThread(**dummy_setting)
    frame = Frame()
    ok_(len(frame.frame_data) == 0)
    worker.add_frame_item(frame, 'myapp', dummy_token, {'alert': 'hello'}, expiry=None, priority=10)

    hex_frame = b2a_hex(str(frame.frame_data))
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


def test_increment_count():
    q = Queue()
    worker = SendWorkerThread(**{
        'task_queue': q,
        'name': 'test_thread',
        'use_sandbox': True,
        'cert_file': 'dummy.cert',
        'key_file': 'dummy.key'
    })
    worker.count = 99
    worker.send = mock.Mock()
    worker.check_error = mock.Mock()
    q.put({
        'appid': 'unittest',
        'token': dummy_token,
        'aps': {'alert': 'Hello'}
    })
    q.put({
        'appid': 'unittest',
        'token': dummy_token,
        'aps': {'alert': 'Woooooooooo'}
    })
    worker.main()
    eq_(101, worker.count, 'worker.count should incremented by messages')


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
