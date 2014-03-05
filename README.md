# APNS-Proxy-Server

デバイストークンを受けて、APNsに流すサーバー

## Requirements

- Python > 2.6

## Setup

```
# APNsへの接続に利用するSSL証明書の配置
cp xxxxx.certs ./certifications/
cp xxxxx.key ./certifications/

# 設定ファイルの作成
cp settings.template.py settings.py
vim settings.py

# Python環境の構築
make setup
```

## 起動

```
apns-proxy-server.sh start
```

## 開発用のコマンド

Command | Description
--- | ---
make setup | Setup python environment
make lint | Check coding style using flake8. Need flake8 on your $PATH
make test | Run Tests
make live_test | Run test using server and client
make run | Run server

