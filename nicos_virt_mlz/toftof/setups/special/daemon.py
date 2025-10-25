description = 'setup for the execution daemon'

group = 'special'

import hashlib

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'sha1',
        # first entry is the user name, second the hashed password, third the user level
        passwd = [
            ('guest', '', 'guest'),
            ('user', hashlib.sha1(b'user').hexdigest(), 'user'),
            ('admin', hashlib.sha1(b'admin').hexdigest(), 'admin'),
        ],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        authenticators = ['Auth'],
        server = configdata('config_data.daemon_bind'),
        loglevel = 'info',
    ),
)
