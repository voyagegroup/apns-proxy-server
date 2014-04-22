# -*- coding: utf-8 -*-

import time

from apns_proxy_client import APNSProxyClient

valid_token = "YOUR VALID TOKEN"


def main():
    client = APNSProxyClient(host="localhost", port=5556, application_id="myapp")
    i = 0

    with client:
        token = valid_token

        client.send(token, 'Alert with default sound')

        time.sleep(2)

        client.send(token, 'Alert with custom sound', sound='custom')

        time.sleep(2)

        client.send(token, 'I am silent', sound=None)

        time.sleep(2)

        client.send(token, 'Alert with badge', badge=2)

        time.sleep(2)

        client.send(token, None, badge=99, sound=None)

        time.sleep(2)

        one_hour_later = int(time.time()) + (60 * 60)
        client.send(token, 'I am long life', expiry=one_hour_later)

        time.sleep(2)

        client.send(token, 'I am low priority', priority=5)

        time.sleep(2)

        # For background fetch
        client.send(token, None, sound=None, content_available=True)

        time.sleep(2)

        client.send(token, 'With custom field', custom={
            'foo': True,
            'bar': [200, 300],
            'boo': "Hello"
        })
        
        time.sleep(2)

        client.send(token, {
            'body': 'This is JSON alert',
            'action_loc_key': None,
            'loc_key': 'loc key',
            'loc_args': ['one', 'two'],
            'launch_image': 'aa.png'
        })

        client.send(token, 'This message never send to device', test=True)


if __name__ == "__main__":
    main()
    print("Done")
