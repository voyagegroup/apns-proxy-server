# -*- coding: utf-8 -*-
"""
Tests for apns_proxy_server.feedback
"""

from datetime import datetime

from nose.tools import ok_, eq_
import simplejson as json

from apns_proxy_server.feedback import FeedbackProxy


def test_instance():
    proxy = FeedbackProxy(True, '/path/to/cert', '/path/to/key')
    ok_(proxy)
    ok_(proxy.use_sandbox)
    eq_(proxy.cert_file, '/path/to/cert')
    eq_(proxy.key_file, '/path/to/key')


def test_get():
    disabled_datetime = datetime(1988, 4, 23, 2, 0, 0)

    proxy = FeedbackProxy(True, '/path/to/cert', '/path/to/key')
    proxy._apns = type('MockApns', (object,), {
        'feedback_server': {
            'token_value': disabled_datetime,
        },
    })

    result = proxy.get()
    json_result = json.loads(result)

    ok_(result)
    ok_(json_result)
    ok_(isinstance(result, basestring))
    ok_(isinstance(json_result, dict))

    ok_('token_value' in json_result)
    eq_(datetime.fromtimestamp(json_result['token_value']), disabled_datetime)
