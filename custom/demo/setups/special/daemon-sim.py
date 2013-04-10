description = 'setup for the execution daemon'
group = 'special'

import hashlib

devices = dict(
    Auth   = device('services.daemon.auth.Authenticator'),
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'localhost:1302',
                    simmode = True,
                    authenticators = ['Auth'],
                    loglevel = 'debug',
                   ),
)
