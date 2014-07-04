# -*- coding: utf-8 -*-
import logging
import logging.config
import traceback

from .server import APNSProxyServer
from . import validator
import settings


def main():
    try:
        logging.config.fileConfig('logging.conf')
        s = validator.validate_settings(settings)
        server = APNSProxyServer(s)
        server.start()
    except Exception, e:
        logging.error(e)
        logging.error(traceback.format_exc())


if __name__ == "__main__":
    main()
