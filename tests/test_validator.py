# -*- coding: utf-8 -*-

import os.path

from nose.tools import eq_, raises

from apns_proxy_server import validator
import tests.data.error_settings1
import tests.data.error_settings2
import tests.data.error_settings3
import tests.data.error_settings4
import tests.data.valid_settings


@raises(ValueError)
def test_invalid_settings1():
    validator.validate_settings(tests.data.error_settings1)


@raises(ValueError)
def test_invalid_settings2():
    validator.validate_settings(tests.data.error_settings2)


@raises(ValueError)
def test_invalid_settings3():
    validator.validate_settings(tests.data.error_settings3)


@raises(ValueError)
def test_invalid_settings4():
    validator.validate_settings(tests.data.error_settings4)


def test_valid_settings():
    validator.validate_settings(tests.data.valid_settings)


def test_path_changed_abs_path():
    s = validator.validate_settings(tests.data.valid_settings)
    for app in s.APPLICATIONS:
        eq_(True, os.path.isabs(app.get('cert_file')))
        eq_(True, os.path.isabs(app.get('key_file')))
