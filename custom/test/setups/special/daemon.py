description = 'setup for the execution daemon'
group = 'special'

import hashlib

devices = dict(
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'localhost',
                    authmethod = 'list',
                    passwd = [('guest', '', 0),
                              ('user', hashlib.sha1('user').hexdigest(), 10),
                              ('admin', hashlib.sha1('admin').hexdigest(), 20)],
                    loglevel = 'debug',
                   ),
)
