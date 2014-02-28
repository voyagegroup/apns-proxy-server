# -*- coding: utf-8 -*-

import logging

from .client import APNSProxyClient

def main():
    client = APNSProxyClient(address="tcp://localhost:5556", application_id="14")
    with client:
        print("start send roop 1")
        cnt = 0
        for i in xrange(10):
            print(i)
            cnt += 1
            token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec1"
            msg = u"これはメッセージです" + str(cnt)
            print("send %s" % token)
            client.send(token, msg)


    client2 = APNSProxyClient(address="tcp://localhost:5556", application_id="13")
    with client2:
        print("start send roop 2")
        cnt = 0
        for i in xrange(10):
            print(i)
            cnt += 1
            token = "b7ae2fcdb2dxxxxxxxxxxxxxxxxxxxxxxx72576d43677544778c43a674407ec1"
            msg = u"これは15へのメッセージです" + str(cnt)
            print("send %s" % token)
            client2.send(token, msg)


    print("Out of with")

if __name__ == "__main__":
    main()
