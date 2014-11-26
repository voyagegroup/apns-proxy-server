# APNs Proxy Server

Proxy server for Apple Push Notification service.

[![Build Status](https://travis-ci.org/voyagegroup/apns-proxy-server.png?branch=master)](https://travis-ci.org/voyagegroup/apns-proxy-server)

### Features

- Multi-Application Support
- Use Extended format (Can use expiry and priority field)
- Check error response automatically
- Client library for Python and more...
- Keep TCP connection while sending payloads for performance.
- Read feedback service

### Handling Error Responses

Read error response when sending queue become empty or each 500 items.
If error response found, re-connect to APNs and retry after the invalid item.

## Requirements

- Python > 2.6
- (optional) gcc, gcc-c++, python-devel, uuid-devel, libuuid-devel and git to compile libzmq on CentOS

## Setup

```
git clone git@github.com:voyagegroup/apns-proxy-server.git
cd apns-proxy-server

# Setup python environment using requirements_prod.txt (@see Makefile)
make setup_prod

# Puts your ssl certs for APNs
cp xxxxx.certs ./apns_certs/
cp xxxxx.key ./apns_certs/

# Make your settings by settings.template.py
cp settings.template.py settings.py
vim settings.py

# Make your logging.conf by logging.conf.template
cp logging.conf.template logging.conf
vim logging.conf
```

## Launch

```
./apns_proxy_server.sh start
```

## How to use

Please see [client repository](https://github.com/voyagegroup/apns-proxy-client-py) or examples folder.

## Dev Commands

Command | Description
--- | ---
make setup | Setup python environment for development
make lint | Check coding style using flake8
make test | Run Tests
make run | Run server

## License

BSD
