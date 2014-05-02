# APNs Proxy Server

Proxy server for Apple Push Notification service.

[![Build Status](https://travis-ci.org/voyagegroup/apns-proxy-server.png?branch=master)](https://travis-ci.org/voyagegroup/apns-proxy-server)

### Features

- Multi-Application Support
- Use Extended format (Can use expiry and priority field)
- Check error response automatically
- Client library for Python and more...
- Keep TCP connection while sending payloads for performance.

### Under development

- Check feedback service

### Handling Error Responses

Read error response when sending queue become empty or each 500 items.
If error response found, re-connect to APNs and retry after the invalid item.

## Requirements

- Python > 2.6

## Setup

```
git clone git@github.com:voyagegroup/apns-proxy-server.git
cd apns-proxy-server

# Setup python environment using requirements_prod.txt (@see Makefile)
make setup_prod

# Puts your ssl certs for APNs
cp xxxxx.certs ./certifications/
cp xxxxx.key ./certifications/

# Make your settings by settings.template.py
cp settings.template.py settings.py
vim settings.py
```

## Launch

```
apns-proxy-server.sh start
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
