#  -*- coding: utf-8 -*-

name = 'setup for the execution daemon'

group = 'special'

import hashlib


devices = dict(
    UserDBAuth = device('frm2.proposaldb.Authenticator',
                        description = 'FRM-II user office authentication',
                       ),
    Auth       = device('services.daemon.auth.ListAuthenticator',
                        description = 'Authentication device',
                        hashing = 'md5',
                        # first entry is the user name, second the hashed password, third the user level
                        passwd = [('guest', '', 'guest'),
                                  ('user', hashlib.md5(b'user').hexdigest(), 'user'),
                                  ('admin', hashlib.md5(b'admin').hexdigest(), 'admin'),
                                 ],
                       ),
    Daemon = device('services.daemon.NicosDaemon',
                    description = 'Daemon, executing commands and scripts',
                    server = '0.0.0.0',
                    authenticators = ['UserDBAuth', 'Auth',],
                    loglevel = 'debug',
                   ),
)
