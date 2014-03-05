# -*- coding: utf-8 -*-

import logging
import time

from .client import APNSProxyClient

def main():
    client = APNSProxyClient(host="localhost", port=5556, application_id="14")
    with client:
        token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ecc"
        i = 0
        interval = 3
        while i < 1000:
            i += 1
            client.send(token, u"☆この案件ありますお☆" + str(i), badge=i)
            print("Send %i" % i)
            if interval < 60:
                interval += 3
            time.sleep(interval)


    print("Out of with")

if __name__ == "__main__":
    main()
