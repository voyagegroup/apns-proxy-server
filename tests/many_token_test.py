# -*- coding: utf-8 -*-

import logging
import time
import threading

from .client import APNSProxyClient

def con1():
    client = APNSProxyClient(address="tcp://localhost:5556", application_id="14")
    with client:
        print("start send roop 1")
        cnt = 0
        for i in xrange(100000):
            cnt += 1
            token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec1"
            msg = u"これはメッセージです" + str(cnt)
            client.send_more(token, msg, badge=1, test=True)
            if i % 3000 == 0:
                client.flush()
                print("Con1 Sended %i" % i)

def con2():
    client = APNSProxyClient(address="tcp://localhost:5556", application_id="14")
    with client:
        print("start send roop 2")
        cnt = 0
        for i in xrange(100000):
            cnt += 1
            token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec1"
            msg = u"これはメッセージです" + str(cnt)
            client.send_more(token, msg, badge=1, test=True)
            if i % 3000 == 0:
                client.flush()
                print("Con2 Sended %i" % i)


#def con3():
#    client = APNSProxyClient(address="tcp://localhost:5556", application_id="13")
#    with client:
#        print("start send roop 3")
#        cnt = 0
#        for i in xrange(100):
#            cnt += 1
#            token = "b7ae2fcdb2dxxxxxxxxxxxxxxxxxxxxxxx72576d43677544778c43a674407ec1"
#            msg = u"これは15へのメッセージです" + str(cnt)
#            client.send_more(token, msg, badge=1, test=True)
#            if i % 3000 == 0:
#                client.flush()
#                print("Sended %i" % i)


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
