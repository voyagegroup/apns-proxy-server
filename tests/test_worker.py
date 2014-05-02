# -*- coding: utf-8 -*-
"""
Tests for apns_proxy_server.worker
"""
from Queue import Queue

from nose.tools import ok_, raises
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
    ok_(len(frame.frame_data) > 0)


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
