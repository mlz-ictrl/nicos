description = 'setup for the execution daemon'

group = 'special'

import hashlib

devices = dict(
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'tofhw.toftof.frm2',
                    authmethod = 'list',
                    passwd = [('guest', '', 'guest'),
                              ('user', hashlib.sha1('user').hexdigest(), 'user'),
                              ('root', '162201b83ecfc640017d93ca11e4f586d0351a16', 'admin'),
                             ],
                    loglevel = 'info',
                   ),
)
