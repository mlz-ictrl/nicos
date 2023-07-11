description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    UserDBAuth = device('nicos_mlz.devices.ghost.Authenticator',
         description = 'FRM II user office authentication',
         instrument = 'ANTARES',
         ghosthost = 'ghost.mlz-garching.de',
         aliases = {
             'ms': ('michael.schulz@frm2.tum.de', 'admin'),
         },
         loglevel = 'info',
    ),
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = [
            'ldap://antaressrv.antares.frm2.tum.de',
        ],
        bindmethod = 'tls_before_bind',
        userbasedn = 'ou=People,dc=antares,dc=frm2,dc=tum,dc=de',
        groupbasedn = 'ou=Group,dc=antares,dc=frm2,dc=tum,dc=de',
        grouproles = {
            'antares': 'admin',
        },
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
            'antares': 'admin',
            'ictrl': 'admin',
            'se': 'guest',
        }
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        description = 'Daemon, executing commands and scripts',
        server = '0.0.0.0',
        authenticators = ['UserDBAuth', 'LDAPAuth', 'LDAPAuthBU', ],
        loglevel = 'debug',
    ),
)
