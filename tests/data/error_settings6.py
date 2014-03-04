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
        "cert_file": "sample.cert",
        "key_file": "no_file.key"
    }
]
