# -*- coding: utf-8 -*-

import logging
import Queue
import socket
import time
import threading
import traceback
from binascii import b2a_hex
from struct import unpack

from apns import APNs, Payload, Frame


class APNsError(Exception):
    """
    Apple Push Notificationサービスからのエラーレスポンスを表現する例外クラス
    --------------------------
    ステータスコード
    --------------------------
      0 エラーなし
      1 処理エラー
      2 デバイストークン欠如
      3 トピック欠如
      4 ペイロード欠如
      5 無効なトークンサイズ
      6 無効なトピックサイズ
      7 無効なペイロードサイズ
      8 無効なトークン
     10 シャットダウン
    255 なし(不明)
    --------------------------
    @see https://developer.apple.com/jp/devcenter/ios/library/documentation/RemoteNotificationsPG.pdf
    """
    def __init__(self, status_code, token_idx):
        self.status_code = status_code
        self.token_idx = token_idx
        self.msg = 'Invalid token found. Status: %s' % status_code

    def __str__(self):
        return self.msg


class SendWorkerThread(threading.Thread):
    """
    APNs送信用のワーカースレッド
    """

    # 送信済みのアイテムを保持する数
    # APNsからはエラーが非同期で得られるのでリトライ用に送信後しばらくは保持しておく必要がある
    KEEP_SENDED_ITEMS_NUM = 2000

    # タスクキューのタイムアウト (sec)
    # 暇な時はリモートサーバーとの接続を切っておくのに使う
    TASK_QUEUE_TIMEOUT = 5 * 60  # 10min

    def __init__(self, task_queue, name, use_sandbox, cert_file, key_file):
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.task_queue = task_queue
        self.name = name

        self.use_sandbox = use_sandbox
        self.cert_file = cert_file
        self.key_file = key_file
        self._apns = None

        self.count = 0
        self.recent_sended = {}

    @property
    def apns(self):
        if self._apns is None:
            self._apns = APNs(
                use_sandbox=self.use_sandbox,
                cert_file=self.cert_file,
                key_file=self.key_file
            )
        return self._apns

    def clear_connection(self):
        self._apns = None

    def run(self):
        while True:
            try:
                while True:
                    self.main()
            except Queue.Empty:
                pass
            except socket.error, e:
                logging.warn(e)
                logging.warn(traceback.format_exc())
                # 考えられるエラー
                # (1) 不正なトークンを送ったことにより、接続を切られた
                #     (self.error_checkでエラーを確認してこちらから切るよりも先に切られた)
                # (2) コネクションを長く張りすぎた事により、接続を切られた
                # どちらにしろ、どこまで送信成功したか判断できないので最後の一個だけリトライする
                self.retry_last_one()
            finally:
                self.clear_connection()

    def main(self):
        item = self.task_queue.get(True, self.TASK_QUEUE_TIMEOUT)
        #logging.debug("%s %s" % (self.name, item))
        self.count += 1
        self.store_item(self.count, item)
        self.send(item['token'], item.get('aps'), item.get('test'))
        self.error_check()

    def store_item(self, idx, item):
        self.recent_sended[idx] = item
        if idx > self.KEEP_SENDED_ITEMS_NUM:
            self.recent_sended.pop(idx - self.KEEP_SENDED_ITEMS_NUM)

    def send(self, token, aps, test=False):
        if test is True:
            return
        logging.debug('Send %s' % token)
        self.apns.gateway_server.send_notification_multiple(
            self.create_frame(token, self.count, **aps)
        )

    def retry_last_one(self):
        self.retry_from(self.count)

    def retry_from(self, start_token_idx):
        """
        リトライするために、タスクキューにアイテムを追加する
        """
        idx = start_token_idx
        while idx <= self.count:
            self.task_queue.put(self.recent_sended[idx])
            idx += 1

    def create_frame(self, token, identifier, alert, sound, badge, expiry):
        payload = Payload(alert=alert, sound=sound, badge=badge)
        priority = 10
        if expiry is None:
            expiry = int(time.time()) + (60 * 60)  # 1 hour
        frame = Frame()
        frame.add_item(token, payload, identifier, expiry, priority)
        return frame

    def error_check(self):
        if self.task_queue.empty() or (self.count % 500 == 0):
            try:
                logging.debug('%s Check error response %i' % (self.name, self.count))
                self.check_apns_error_response()
            except APNsError, ape:
                logging.warn(ape.msg)
                # 不正なトークン、リモートサーバーからは接続が切られるので、再接続する
                self.clear_connection()
                if ape.token_idx in self.recent_sended:
                    # 不正なトークン以降に送った物は、送信できていないので再送する
                    logging.warn("Invalid token found %s", self.recent_sended[ape.token_idx]['token'])
                    self.retry_from(ape.token_idx + 1)
                else:
                    # recent_sendedから消した過去のtokenがエラーとして得られた場合
                    # どうにもできない
                    pass

    def check_apns_error_response(self):
        """
        APNsのエラーレスポンスをチェックする
        エラーが無い時はタイムアウトする

        TODO
        ここにあるのも違和感なので、PyAPNSに追加してPullRequestを送る。
        """
        if self.apns.gateway_server._socket is None:
            logging.warn("Connection has not established")
            return

        try:
            self.apns.gateway_server._socket.settimeout(0.5)
            error_bytes = self.apns.gateway_server.read(6)
            if len(error_bytes) < 6:
                return

            command = b2a_hex(unpack('>c', error_bytes[0:1])[0])
            if command != '08':
                logging.warn('Unknown command received %s', command)
                return
            status = b2a_hex(unpack('>c', error_bytes[1:2])[0])
            identifier = unpack('>I', error_bytes[2:6])[0]
            raise APNsError(status, identifier)

        except socket.error, e:
            if isinstance(e.args, tuple):
                if e[0] == 'The read operation timed out':
                    return  # No error response.
            logging.warn(e)
