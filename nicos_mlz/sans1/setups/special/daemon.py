description = 'setup for the execution daemon'
group = 'special'

devices = dict(
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
        },
    ),
    UserDB = device('nicos_mlz.devices.proposaldb.Authenticator'),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = 'sans1ctrl.sans1.frm2',
        authenticators = ['LDAPAuth', 'UserDB'],
        loglevel = 'debug',
    ),
)
