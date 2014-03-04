# -*- coding: utf-8 -*-

import logging
import time

from .client import APNSProxyClient

def main():
    client = APNSProxyClient(address="tcp://localhost:5556", application_id="14")
    with client:
        token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ecc"
        client.send(token, u"☆この案件あります☆", badge=9999)
        time.sleep(0.5)
        token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec1"
        client.send(token, u"☆この案件あります☆", badge=9999)
        time.sleep(0.5)

        token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ecc"
        i = 0
        while i < 5:
            i += 1
            client.send(token, u"☆この案件ありますお☆" + str(i), badge=i)
            time.sleep(1)

#    client = APNSProxyClient(address="tcp://localhost:5556", application_id="14")
#    with client:
#        print("start send roop 1")
#        cnt = 0
#        for i in xrange(100000):
#            cnt += 1
#            token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec1"
#            msg = u"これはメッセージです" + str(cnt)
#            client.send(token, msg, badge=1, test=True)
#
#    client = APNSProxyClient(address="tcp://localhost:5556", application_id="14")
#    with client:
#        print("start send roop 1")
#        cnt = 0
#        for i in xrange(100000):
#            cnt += 1
#            token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec1"
#            msg = u"これはメッセージです" + str(cnt)
#            client.send(token, msg, badge=1, test=True)
#

#    client2 = APNSProxyClient(address="tcp://localhost:5556", application_id="13")
#    with client2:
#        print("start send roop 2")
#        cnt = 0
#        for i in xrange(100):
#            cnt += 1
#            token = "b7ae2fcdb2dxxxxxxxxxxxxxxxxxxxxxxx72576d43677544778c43a674407ec1"
#            msg = u"これは15へのメッセージです" + str(cnt)
#            client2.send(token, msg, test=True)


    print("Out of with")

if __name__ == "__main__":
    main()
