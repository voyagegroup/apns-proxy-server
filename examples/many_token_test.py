# -*- coding: utf-8 -*-

import time
import threading

from apns_proxy_client import APNSProxyClient


def con1():
    client = APNSProxyClient(host="localhost", port=5556, application_id="14")
    with client:
        print("start send roop 1")
        cnt = 0
        msg = u"これはメッセージです"
        for i in xrange(100000):
            cnt += 1
            token = "a7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec1"
            client.send(token, msg, badge=1, test=True)
            if i % 3000 == 0:
                print("Con1 Sended %i" % i)


def con2():
    client = APNSProxyClient(host="localhost", port=5556, application_id="14")
    with client:
        print("start send roop 2")
        cnt = 0
        for i in xrange(100000):
            cnt += 1
            token = "a7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec1"
            msg = u"これはメッセージです" + str(cnt)
            client.send(token, msg, badge=1, test=True)
            if i % 3000 == 0:
                print("Con2 Sended %i" % i)


def main():
    print("Start connection")
    start_time = time.time()
    thread1 = threading.Thread(target=con1)
    thread2 = threading.Thread(target=con2)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    end_time = time.time()
    print("Passed %f sec" % (end_time - start_time))

if __name__ == "__main__":
    main()
