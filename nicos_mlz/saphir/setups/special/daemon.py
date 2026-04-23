description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    UserDBAuth = device('nicos_mlz.devices.ghost.Authenticator',
         description = 'FRM II user office authentication',
         instrument = 'SAPHiR',
         ghosthost = 'ghost.mlz-garching.de',
         aliases = {
         },
         loglevel = 'info',
    ),
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = [
            'ldap://saphirsrv.saphir.frm2.tum.de',
        ],
        bindmethod = 'tls_before_bind',
        userbasedn = 'ou=People,dc=saphir,dc=frm2,dc=tum,dc=de',
        groupbasedn = 'ou=Group,dc=saphir,dc=frm2,dc=tum,dc=de',
        grouproles = {
            'saphir': 'admin',
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
            'saphir': 'admin',
            'ictrl': 'admin',
            'se': 'user',
        }
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['UserDBAuth', 'LDAPAuth', 'LDAPAuthBU',],
        loglevel = 'info',
    ),
)
