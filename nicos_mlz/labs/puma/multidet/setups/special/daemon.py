description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
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
            'puma': 'admin',
            'ictrl': 'admin',
        }
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        authenticators = ['LDAPAuth'],
        server = '',
        loglevel = 'info',
    ),
)
