#  -*- coding: utf-8 -*-

description = 'setup for the execution daemon'

group = 'special'

devices = dict(
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = 'ldap://phaidra.admin.frm2',
        userbasedn = 'ou=People,dc=frm2,dc=de',
        groupbasedn = 'ou=Group,dc=frm2,dc=de',
        grouproles = {
            'antares': 'admin',
            'ictrl': 'admin',
            'se': 'guest',
        }
    ),
    UserDBAuth = device('nicos_mlz.devices.ghost.Authenticator',
         description = 'FRM II user office authentication',
         instrument = 'ANTARES',
         ghosthost = 'ghost.mlz-garching.de',
         aliases = {
             'ms': ('michael.schulz@frm2.tum.de', 'admin'),
         },
         loglevel = 'info',
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        description = 'Daemon, executing commands and scripts',
        server = '0.0.0.0',
        authenticators = [
            'LDAPAuth',
            'UserDBAuth',
        ],
        loglevel = 'debug',
    ),
)
