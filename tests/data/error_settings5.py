# -*- coding: utf-8 -*-

import logging

LOG_LEVEL = logging.INFO

# クライアントを待ちうけるポート
BIND_PORT_FOR_ENTRY = 5556
# PUSH-PULL用のポート
BIND_PORT_FOR_PULL = 5557

# アプリ毎のワーカースレッドの数
THREAD_NUMS_PER_APPLICATION = 5

# アプリ毎のAPNsの設定
APPLICATIONS = [
    {
        "application_id": "14",
        "name": "My App1",
        "sandbox": False,
        "cert_file": "no_file.cert",
        "key_file": "sample.key"
    }
]
