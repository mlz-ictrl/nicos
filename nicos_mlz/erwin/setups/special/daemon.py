description = 'setup for the execution daemon'

group = 'special'

import hashlib

devices = dict(
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = 'ldap://phaidra.admin.frm2',
        userbasedn = 'ou=People,dc=frm2,dc=de',
        groupbasedn = 'ou=Group,dc=frm2,dc=de',
        grouproles = {
            'erwin': 'admin',
            'ictrl': 'admin',
            'se': 'user',
        },
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        authenticators = ['LDAPAuth'],
        loglevel = 'info',
        server = '',
    ),
)
