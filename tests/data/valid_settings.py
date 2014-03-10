# -*- coding: utf-8 -*-

import logging
import os.path

LOG_LEVEL = logging.INFO

# クライアントを待ちうけるポート
BIND_PORT_FOR_ENTRY = 4556
# PUSH-PULL用のポート
BIND_PORT_FOR_PULL = 4557

# アプリ毎のワーカースレッドの数
THREAD_NUMS_PER_APPLICATION = 5

#################################################################
# 絶対パスを作るための準備 (Unit test用)
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../')
CERT_DIR = os.path.join(BASE_DIR, 'apns_certs')
#################################################################

# アプリ毎のAPNsの設定
APPLICATIONS = [
    {
        "application_id": "14",
        "name": "My App1",
        "sandbox": False,
        "cert_file": "sample.cert",
        "key_file": "sample.key"
    },
    {
        "application_id": "13",
        "name": "My App2",
        "sandbox": False,
        "cert_file": os.path.join(CERT_DIR, "sample.cert"),
        "key_file": os.path.join(CERT_DIR, "sample.key")
    }
]
