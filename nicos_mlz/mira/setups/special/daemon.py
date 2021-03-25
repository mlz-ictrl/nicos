description = 'setup for the daemon'
group = 'special'

devices = dict(
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = 'ldap://phaidra.admin.frm2',
        userbasedn = 'ou=People,dc=frm2,dc=de',
        groupbasedn = 'ou=Group,dc=frm2,dc=de',
        grouproles = {
            'mira': 'admin',
            'ictrl': 'admin',
            'se': 'user',
        }
    ),
    UserDBAuth = device('nicos_mlz.devices.ghost.Authenticator',
         description = 'FRM II user office authentication',
         instrument = 'MIRA',
         ghosthost = 'ghost.mlz-garching.de',
         aliases = {
            'robertg': ('robert.georgii@frm2.tum.de', 'admin'),
         },
         loglevel = 'info',
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = 'miractrl.mira.frm2',
        loglevel = 'info',
        authenticators = ['LDAPAuth', 'UserDBAuth']
    ),
)
