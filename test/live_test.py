# -*- coding: utf-8 -*-

from .client import APNSProxyClient

def main():
    client = APNSProxyClient(address="tcp://localhost:5556", application_id="14")
    with client:
        #for i in xrange(100000):
        print("start send roop")
        cnt = 0
        for i in xrange(100000):
            cnt += 1
            token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec1"
            msg = u"これはメッセージです" + str(cnt)
            client.send(token, msg)

        ret = client.result()
        print("Received %s" % ret)
        print("Send %i times" % cnt)

    print("Out of with")

if __name__ == "__main__":
    main()
