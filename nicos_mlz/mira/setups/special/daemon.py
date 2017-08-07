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
        }
    ),
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'md5',
        passwd = [
            ('admin', 'cf5bdfb40421ac1f30cc4d45b66b5a81', 'admin'),
            ('', '', 'user'),
        ],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = 'mira1',
        loglevel = 'info',
        authenticators = ['LDAPAuth', 'Auth']
    ),
)
