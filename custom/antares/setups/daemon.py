#  -*- coding: utf-8 -*-

name = 'setup for the execution daemon'
group = 'special'

import hashlib

devices = dict(
    Daemon = device('nicos.daemon.NicosDaemon',
                    server = 'localhost',
                    authmethod = 'list',
                    passwd = [('guest', '', 0),
                              ('user', hashlib.sha1('user').hexdigest(), 1),
                              ('root', hashlib.sha1('root').hexdigest(), 2)],
                    loglevel = 'debug'),
)
