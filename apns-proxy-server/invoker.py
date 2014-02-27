# -*- coding: utf-8 -*-

import logging
import traceback

from . import server
import settings


def init_log(level):
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(levelname)s %(message)s')


def main():
    try:
        init_log(settings.LOG_LEVEL)
        logging.info('Start server on %s' % settings.BIND_ADDRESS)
        server.start(settings.BIND_ADDRESS)
    except Exception, e:
        logging.error(e)
        logging.error(traceback.format_exc())


if __name__ == "__main__":
    main()
