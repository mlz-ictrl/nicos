description = 'setup for the execution daemon'
group = 'special'

import hashlib

devices = dict(
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'tasgroup2.taco.frm2',
                    authmethod = 'list',
                    passwd = [('guest', '', 0),
                              ('user', hashlib.sha1('user').hexdigest(), 1),
                              ('root', hashlib.sha1('root').hexdigest(), 2)],
                    loglevel = 'info'),
)
