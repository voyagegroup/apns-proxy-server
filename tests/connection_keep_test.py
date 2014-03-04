# -*- coding: utf-8 -*-

import logging
import time

from .client import APNSProxyClient

def main():
    client = APNSProxyClient(address="tcp://localhost:5556", application_id="14")
    with client:
        token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ecc"
        i = 0
        interval = 1
        while i < 3:
            i += 1
            client.send(token, u"☆この案件ありますお☆" + str(i), badge=i)
            print("Send %i" % i)
            print("Sleep %i" % interval)
            time.sleep(interval)
            interval = interval * 2


    print("Out of with")

if __name__ == "__main__":
    main()
