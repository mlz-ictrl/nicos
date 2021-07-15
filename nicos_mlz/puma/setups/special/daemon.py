description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    UserDBAuth = device('nicos_mlz.devices.ghost.Authenticator',
         description = 'FRM II user office authentication',
         instrument = 'PUMA',
         ghosthost = 'ghost.mlz-garching.de',
         aliases = {
         },
         loglevel = 'info',
    ),
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = 'ldap://phaidra.admin.frm2',
        userbasedn = 'ou=People,dc=frm2,dc=de',
        groupbasedn = 'ou=Group,dc=frm2,dc=de',
        grouproles = {
            'puma': 'admin',
            'ictrl': 'admin',
            'se': 'user',
        }
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = 'pumahw.puma.frm2',
        authenticators = ['UserDBAuth', 'LDAPAuth'],
        loglevel = 'debug',
    ),
)
