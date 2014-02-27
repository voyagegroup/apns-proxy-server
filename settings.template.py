# -*- coding: utf-8 -*-

import logging

LOG_LEVEL = logging.INFO

BIND_ADDRESS = "tcp://*:5556"

APPLICATIONS = {
    "app1": {
        "application_id": "14",
        "cert_file": "hoge.cert",
        "key_file": "fuga.key"
    },
    "app2": {
        "application_id": "13",
        "cert_file": "bar.cert",
        "key_file": "buz.key"
    }
}
