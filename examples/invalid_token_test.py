# -*- coding: utf-8 -*-
"""
Server output logs when invalid token received
"""

import time

from apns_proxy_client import APNSProxyClient

valid_token = "YOUR_VALID_TOKEN"
invalid_token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec1"


def main():
    client = APNSProxyClient(host="localhost", port=5556, application_id="14")
    with client:
        i = 1
        client.send(valid_token, "This message should reach " + str(i), badge=i)
        i += 1
        client.send(valid_token, "This message should reach " + str(i), badge=i)
        i += 1
        client.send(invalid_token, "error" + str(i), badge=i)

        time.sleep(2)

        i += 1
        client.send(valid_token, "This message should reach " + str(i), badge=i)
        i += 1
        client.send(valid_token, "This message should reach " + str(i), badge=i)

        time.sleep(2)

        i += 1
        client.send(invalid_token, "error" + str(i), badge=i)

        time.sleep(0.5)

        i += 1
        client.send(valid_token, "This message should reach " + str(i), badge=i)

        time.sleep(0.5)

        i += 1
        client.send(valid_token, "This message should reach " + str(i), badge=i)

        time.sleep(0.5)

        i += 1
        client.send(valid_token, "This message should reach " + str(i), badge=i)


if __name__ == "__main__":
    main()
