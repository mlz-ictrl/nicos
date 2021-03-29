description = 'setup for the execution daemon'

group = 'special'

devices = dict(
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = 'ldap://phaidra.admin.frm2',
        userbasedn = 'ou=People,dc=frm2,dc=de',
        groupbasedn = 'ou=Group,dc=frm2,dc=de',
        grouproles = {
            'toftof': 'admin',
            'ictrl': 'admin',
            'se': 'user',
        },
    ),
    UserDBAuth = device('nicos_mlz.devices.ghost.Authenticator',
         description = 'FRM II user office authentication',
         instrument = 'TOFTOF',
         ghosthost = 'ghost.mlz-garching.de',
         aliases = {
         },
         loglevel = 'info',
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = 'tofhw.toftof.frm2',
        authenticators = ['LDAPAuth', 'UserDBAuth'],
        loglevel = 'info',
    ),
)
