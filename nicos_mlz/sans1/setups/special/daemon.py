description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    UserDBAuth = device('nicos_mlz.devices.ghost.Authenticator',
         description = 'FRM II user office authentication',
         instrument = 'SANS-1',
         ghosthost = 'ghost.mlz-garching.de',
         aliases = {
         },
         loglevel = 'info',
    ),
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = 'ldap://phaidra.admin.frm2',
        userbasedn = 'ou=People,dc=frm2,dc=de',
        groupbasedn = 'ou=Group,dc=frm2,dc=de',
        userroles = {
            'awilhelm': 'admin',
            'aheinema': 'admin',
            'smuehlba': 'admin',
            'sbusch':   'admin',
        },
        grouproles = {
            'sans1': 'user',
            'ictrl': 'admin',
            'se': 'user',
        },
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = 'sans1ctrl.sans1.frm2',
        authenticators = ['UserDBAuth', 'LDAPAuth'],
        loglevel = 'debug',
    ),
)
