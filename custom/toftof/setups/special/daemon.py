description = 'setup for the execution daemon'

group = 'special'

import hashlib

devices = dict(
    Auth   = device('services.daemon.auth.ListAuthenticator',  # or 'frm2.auth.Frm2Authenticator'
                     # first entry is the user name, second the hashed password, third the user level
                    passwd = [('guest', '', 'guest'),
                              ('user', hashlib.sha1('user').hexdigest(), 'user'),
                              ('root', '162201b83ecfc640017d93ca11e4f586d0351a16', 'admin'),
                             ],
                   ),
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'tofhw.toftof.frm2',
                    authenticator = 'Auth',
                    loglevel = 'info',
                   ),
)
