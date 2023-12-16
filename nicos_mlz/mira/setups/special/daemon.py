description = 'setup for the daemon'
group = 'special'

devices = dict(
    UserDBAuth = device('nicos_mlz.devices.ghost.Authenticator',
         description = 'FRM II user office authentication',
         instrument = 'MIRA',
         ghosthost = 'ghost.mlz-garching.de',
         aliases = {
            'robertg': ('robert.georgii@frm2.tum.de', 'admin'),
         },
         loglevel = 'info',
    ),
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = [
            'ldap://mirasrv.mira.frm2.tum.de',
        ],
        bindmethod = 'tls_before_bind',
        userbasedn = 'ou=People,dc=mira,dc=frm2,dc=tum,dc=de',
        groupbasedn = 'ou=Group,dc=mira,dc=frm2,dc=tum,dc=de',
        grouproles = {
            'mira': 'admin',
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
            'mira': 'admin',
            'ictrl': 'admin',
            'se': 'user',
        }
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = 'miractrl.mira.frm2.tum.de',
        loglevel = 'info',
        authenticators = ['UserDBAuth', 'LDAPAuth', 'LDAPAuthBU',],
    ),
)
