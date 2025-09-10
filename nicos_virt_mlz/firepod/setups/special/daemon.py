description = 'setup for the execution daemon'

group = 'special'

import hashlib

devices = dict(
    UserDBAuth = device('nicos_mlz.devices.ghost.Authenticator',
         description = 'FRM II user office authentication',
         instrument = 'FIREPOD',
         ghosthost = 'ghost.mlz-garching.de',
         aliases = {
         },
         loglevel = 'info',
    ),
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'sha1',
        passwd = [
            ('guest', '', 'guest'),
            ('user', hashlib.sha1(b'user').hexdigest(), 'user'),
            ('admin', hashlib.sha1(b'admin').hexdigest(), 'admin'),
        ],
    ),
    LDAPAuthBU = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = [
            'ldap://phaidra.admin.frm2.tum.de',
            'ldap://ariadne.admin.frm2.tum.de',
            'ldap://sarpedon.admin.frm2.tum.de',
            'ldap://minos.admin.frm2.tum.de',
        ],
        bindmethod = 'tls_before_bind',
        userbasedn = 'ou=People,dc=frm2,dc=tum,dc=de',
        groupbasedn = 'ou=Group,dc=frm2,dc=tum,dc=de',
        grouproles = {
            'firepod': 'admin',
            'ictrl': 'admin',
            'se': 'user',
        },
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        authenticators = ['UserDBAuth', 'LDAPAuthBU', 'Auth'],
        loglevel = 'info',
        server = configdata('config_data.daemon_bind'),
    ),
)
