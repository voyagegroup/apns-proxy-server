# APNs Proxy Server

デバイストークンを受けて、Apple Push Notification serviceに流すサーバー

[![Build Status](https://travis-ci.org/genesix/apns-proxy-server.png?branch=master)](https://travis-ci.org/genesix/apns-proxy-server)

### Features

- Multi-Application Support
- Use Extended format (Can use expiry and priority field)
- Check error response automatically
- Check feedback service
- Client library for Python and more...
- High speed client server data transfer by ZMQ socket.

### Handling Error Responses

送信500件毎、もしくは送信キューが空になった時点でAPNsのエラーレスポンスをチェックする。
不正なデバイストークンが混入した事によるコネクションロストに対応するため。
エラーレスポンスが存在した場合、APNsに再接続して該当データ以後の物を自動で再送する。

## Requirements

- Python > 2.6

## Setup

```
# Puts ssl certs for APNs
cp xxxxx.certs ./certifications/
cp xxxxx.key ./certifications/

# Make your settings by settings.template.py
cp settings.template.py settings.py
vim settings.py

# Setup python environment using requirements_prod.txt
make setup_prod
```

## Launch

```
apns-proxy-server.sh start
```

## How to use

Please see [client repository](https://github.com/genesix/apns-proxy-client-py) or examples folder.

## Dev Commands

Command | Description
--- | ---
make setup | Setup python environment for development
make lint | Check coding style using flake8
make test | Run Tests
make run | Run server

## License

BSD
