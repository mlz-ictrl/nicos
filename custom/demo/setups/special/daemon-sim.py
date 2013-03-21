description = 'setup for the execution daemon'
group = 'special'

import hashlib

devices = dict(
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'localhost:1302',
                    simmode = True,
                    authenticator = None,
                    loglevel = 'debug',
                   ),
)
