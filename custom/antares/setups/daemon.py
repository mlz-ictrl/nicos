#  -*- coding: utf-8 -*-

name = 'setup for the execution daemon'
group = 'special'

import hashlib

devices = dict(
    UserDB = device('frm2.auth.Frm2Authenticator'),
    Auth   = device('services.daemon.auth.ListAuthenticator',
                    hashing = 'md5',
                    # first entry is the user name, second the hashed password, third the user level
                    passwd = [('guest', '', 'guest'),
                              ('user', hashlib.md5('user').hexdigest(), 'user'),
                              ('admin', hashlib.md5('admin').hexdigest(), 'admin')],
                   ),
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'localhost',
                    authenticators = ['Auth'], # or ['UserDB', 'Auth']
                    loglevel = 'debug'),
)
