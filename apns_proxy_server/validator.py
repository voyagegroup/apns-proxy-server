# -*- coding: utf-8 -*-
"""
設定ファイルを検証するモジュール
"""

import os.path
import logging


def validate_settings(settings):
    if not hasattr(settings, 'BIND_ADDRESS'):
        raise ValueError('BIND_ADDRESS not found in setttings')
    if not hasattr(settings, 'THREAD_NUMS_PER_APPLICATION'):
        raise ValueError('THREAD_NUMS_PER_APPLICATION not found in settings')
    if not hasattr(settings, 'APPLICATIONS'):
        raise ValueError('APPLICATION not found in settings')
    for app in settings.APPLICATIONS:
        if not 'application_id' in app:
            raise ValueError('application_id not found in application list')
        if not 'name' in app:
            raise ValueError('name not found in application list')
        if not 'sandbox' in app:
            raise ValueError('sandbox not found in application list')
        if not 'cert_file' in app:
            raise ValueError('cert_file not found in application list')
        if not 'key_file' in app:
            raise ValueError('key_file not found in application list')
        path_to_abspath(app)
        check_file_exists(app)
    return settings


def path_to_abspath(app):
    BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
    CERT_DIR = os.path.join(BASE_DIR, 'apns_certs')

    cert_file = app['cert_file']
    if not os.path.isabs(cert_file):
        app['cert_file'] = os.path.join(CERT_DIR, cert_file)

    key_file = app['key_file']
    if not os.path.isabs(key_file):
        app['key_file'] = os.path.join(CERT_DIR, key_file)


def check_file_exists(app):
    if not os.path.isfile(app['cert_file']):
        raise IOError('Certification file not found: %s' % app['cert_file'])

    if not os.path.isfile(app['key_file']):
        raise IOError('Key file not found: %s' % app['key_file'])


