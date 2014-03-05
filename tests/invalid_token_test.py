# -*- coding: utf-8 -*-
"""
不正なトークンが送られた場合はサーバーのログに出力され。
不正なトークン移行の物がリトライされる事を確認する
"""

import logging
import time

from .client import APNSProxyClient

def main():
    client = APNSProxyClient(host="localhost", port=5556, application_id="14")
    with client:
        i = 1
        token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec1"
        client.send(token, u"☆この案件ありますお☆" + str(i), badge=i)
        i += 1
        token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ecc" #valid
        client.send(token, u"☆この案件ありますお☆" + str(i), badge=i)
        i += 1
        token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec2"
        client.send(token, u"☆この案件ありますお☆" + str(i), badge=i)

        time.sleep(2)

        i += 1
        token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ecc" #valid
        client.send(token, u"☆この案件ありますお☆" + str(i), badge=i)
        i += 1
        token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ecc" #valid
        client.send(token, u"☆この案件ありますお☆" + str(i), badge=i)

        time.sleep(2)

        i += 1
        token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ec2"
        client.send(token, u"☆この案件ありますお☆" + str(i), badge=i)

        time.sleep(0.5)

        i += 1
        token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ecc" #valid
        client.send(token, u"☆この案件ありますお☆" + str(i), badge=i)

        time.sleep(0.5)

        i += 1
        token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ecc" #valid
        client.send(token, u"☆この案件ありますお☆" + str(i), badge=i)

        time.sleep(0.5)

        i += 1
        token = "b7ae2fcdb2d325a2de86d572103bff6dd272576d43677544778c43a674407ecc" #valid
        client.send(token, u"☆この案件ありますお☆" + str(i), badge=i)


if __name__ == "__main__":
    main()
