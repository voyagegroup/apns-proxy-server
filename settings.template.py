# -*- coding: utf-8 -*-

import logging

LOG_LEVEL = logging.INFO

# クライアントを待ちうけるポート
BIND_ADDRESS = "tcp://*:5556"

# アプリ毎のワーカースレッドの数
THREAD_NUMS_PER_APPLICATION = 5

# アプリ毎のAPNsの設定
APPLICATIONS = [
    {
        "application_id": "14",
        "name": "My App1",
        "sandbox": False,
        "cert_file": "hoge.cert",  # Put in the ./apns_certs directory
        "key_file": "fuga.key"     # Put in the ./apns_certs direcotry
    },
    {
        "application_id": "13",
        "name": "My App2",
        "sandbox": False,
        "cert_file": "/path/to/certs/apns.cert",
        "key_file": "/path/to/certs/apns.key"
    }
]
