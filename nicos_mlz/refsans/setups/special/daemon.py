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
        },
    ),
    UserDB = device('nicos_mlz.devices.proposaldb.Authenticator'),
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'md5',
        # first entry is the user name, second the hashed password, third the user level
        passwd = [
            ('guest', '', 'guest'),
            ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
        ],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = 'refsansctrl.refsans.frm2.tum.de',
        authenticators = ['LDAPAuth', 'UserDB', 'Auth'],
    ),
)
