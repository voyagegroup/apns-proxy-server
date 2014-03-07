# -*- coding: utf-8 -*-

import logging
import time

from apns_proxy_client import APNSProxyClient

valid_token = "YOUR_VALID_DEVICE_TOKEN"

def main():
    client = APNSProxyClient(host="localhost", port=5556, application_id="14")
    with client:
        token = valid_token
        i = 0
        interval = 120
        while i < 1000:
            i += 1
            client.send(token, 'Hey Hey'+ str(i), badge=i)
            print("Send %i" % i)
            if interval < 20 * 60:
                interval = int(interval * 1.4)
            time.sleep(interval)


if __name__ == "__main__":
    main()
    print("Done")
