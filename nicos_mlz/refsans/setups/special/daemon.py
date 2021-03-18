description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = 'ldap://phaidra.admin.frm2',
        userbasedn = 'ou=People,dc=frm2,dc=de',
        groupbasedn = 'ou=Group,dc=frm2,dc=de',
        grouproles = {
            'refsans': 'admin',
            'ictrl': 'admin',
            'se': 'user',
        },
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['LDAPAuth'],
    ),
)
