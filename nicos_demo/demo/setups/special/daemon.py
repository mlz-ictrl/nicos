description = 'setup for the execution daemon'

group = 'special'

import hashlib

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'sha1',
        # for the meaning of these entries see
        # https://forge.frm2.tum.de/nicos/doc/nicos-stable/services/daemon/#nicos.services.daemon.auth.list.Authenticator
        passwd = [
            ('guest', '', 'guest'),
            ('user', hashlib.sha1(b'user').hexdigest(), 'user'),
            ('admin', hashlib.sha1(b'admin').hexdigest(), 'admin'),
        ],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        authenticators = ['Auth'],
        loglevel = 'debug',
        server = 'localhost',
    ),
)
