# APNS Proxy Server

デバイストークンを受けて、APNsに流すサーバー

[![Build Status](https://travis-ci.org/genesix/apns-proxy-server.png?branch=master)](https://travis-ci.org/genesix/apns-proxy-server)

- Multi-Application Support
- Use Extended format (Can use expiry and priority field)
- Check automatically error response
- Check automatically feedback service
- Native client for Python and more...

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

## How to use

Please see [client repository](https://github.com/genesix/apns-proxy-client-py) or examples folder.

## 開発用のコマンド

Command | Description
--- | ---
make setup | Setup python environment
make lint | Check coding style using flake8
make test | Run Tests
make run | Run server

