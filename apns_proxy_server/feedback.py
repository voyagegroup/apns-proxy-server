# -*- coding: utf-8 -*-

import time

from apns import APNs
import simplejson as json


class FeedbackProxy(object):
    def __init__(self, use_sandbox, cert_file, key_file):
        self.use_sandbox = use_sandbox
        self.cert_file = cert_file
        self.key_file = key_file

        self._apns = APNs(
            use_sandbox=self.use_sandbox,
            cert_file=self.cert_file,
            key_file=self.key_file,
        )

    def get(self):
        conn = self._apns.feedback_server
        result = {}

        for item in conn.items():
            token, datetime = item
            result[token] = time.mktime(datetime.timetuple())

        return json.dumps(result)
