# -*- coding: utf-8 -*-
"""
Tests for worker
"""
from Queue import Queue, Empty

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


def test_create_frame():
    worker = SendWorkerThread(**dummy_setting)
    frame = worker.create_frame(dummy_token, 1, expiry=None, priority=10, alert='Hello')
    ok_(isinstance(frame, Frame))


def test_create_frame_with_full_args():
    worker = SendWorkerThread(**dummy_setting)
    frame = worker.create_frame(dummy_token, 1, expiry=None, priority=10,
                                alert='Hello',
                                sound='default',
                                badge=99,
                                custom={
                                    'foo': 'bar'
                                },
                                content_available=True)
    ok_(isinstance(frame, Frame))


@raises(PayloadTooLargeError)
def test_create_frame_with_too_large_content():
    worker = SendWorkerThread(**dummy_setting)
    frame = worker.create_frame(dummy_token, 1, expiry=None, priority=10,
                                alert='This is too large messageeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
                                sound='default',
                                badge=99,
                                custom={
                                    'foo': 'foooooooooooooooooooooooooooooooooooooooooooooooo',
                                    'bar': 'barrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr',
                                    'buz': 'buzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
                                },
                                content_available=True)
