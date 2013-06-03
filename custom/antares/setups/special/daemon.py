#  -*- coding: utf-8 -*-

name = 'setup for the execution daemon'
group = 'special'

import hashlib


devices = dict(
    Auth   = device('services.daemon.auth.ListAuthenticator',  # or 'frm2.auth.Frm2Authenticator'
                     description = 'Authentication device',
                     # first entry is the user name, second the hashed password, third the user level
                     hashing = 'sha1',
                     passwd = [('guest', '', 'guest'),
                               ('user', hashlib.sha1('user').hexdigest(), 'user'),
                               ('admin', hashlib.sha1('admin').hexdigest(), 'admin')],
                   ),
    Daemon = device('services.daemon.NicosDaemon',
                     description = 'Daemon, executingcommands and scripts',
                     server = '0.0.0.0',
                     authenticators = ['Auth',],
                     loglevel = 'debug',
                   ),
)

