description = 'setup for the execution daemon'
group = 'special'

import hashlib

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'md5',
        passwd = [('guest', '', 'guest'),
                  ('user', hashlib.md5(b'user').hexdigest(), 'user'),
                  ('jcns', hashlib.md5(b'jcns').hexdigest(), 'admin'),
                  ('admin', hashlib.md5(b'admin').hexdigest(), 'admin')],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = 'localhost',
        authenticators = ['Auth'],
        loglevel = 'debug',
    ),
)
