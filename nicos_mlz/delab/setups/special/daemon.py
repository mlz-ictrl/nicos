description = 'setup for the daemon'
group = 'special'

devices = dict(
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = 'ldap://phaidra.admin.frm2',
        userbasedn = 'ou=People,dc=frm2,dc=de',
        groupbasedn = 'ou=Group,dc=frm2,dc=de',
        grouproles = {
            'del': 'admin',
            'ictrl': 'admin',
        }
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '0.0.0.0',
        loglevel = 'info',
        authenticators = ['LDAPAuth'],
    ),
)
