# -*- coding: utf-8 -*-

# Listen ports
BIND_PORT_FOR_ENTRY = 5556
BIND_PORT_FOR_PULL = 5557

# Number of threads per application
THREAD_NUMS_PER_APPLICATION = 5

# APNs settings
APPLICATIONS = [
    {
        "application_id": "14",
        "name": "My App1",
        "sandbox": False,
        "cert_file": "sample.cert",  # Put in the ./apns_certs directory
        "key_file": "sample.key"     # Put in the ./apns_certs direcotry
    },
    {
        "application_id": "13",
        "name": "My App2",
        "sandbox": False,
        "cert_file": "/path/to/certs/apns.cert",  # Or use absolute path
        "key_file": "/path/to/certs/apns.key"
    }
]
