description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = 'ldap://phaidra.admin.frm2',
        userbasedn = 'ou=People,dc=frm2,dc=de',
        groupbasedn = 'ou=Group,dc=frm2,dc=de',
        grouproles = {
            'sans1': 'admin',
            'ictrl': 'admin',
        }
    ),
    UserDB = device('nicos_mlz.frm2.devices.proposaldb.Authenticator'),
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'md5',
        # first entry is the user name, second the hashed password, third the user level
        passwd = [
            ('guest', '', 'guest'),
            ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
            ('admin', 'ec326b6858b88a51ff1605197d664add', 'admin'),
            ('andreas', 'da5121879fff54b08b69ec54d9ac2bf6', 'admin'),
            ('andre', '1b2bc04a135d959e8da04733e24195da', 'admin'),
            ('sebastian', '6c79a7389f572813edfe5fc873e099ce', 'admin'),
            ('sbusch', 'b71e7f18a043b020b4935f6694a918cf', 'admin'),
            ('edv', 'cb50179ebd60c94a29770c652a848765', 'admin'),
        ],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = 'sans1ctrl.sans1.frm2',
        authenticators = ['LDAPAuth', 'UserDB', 'Auth'],
        loglevel = 'debug',
    ),
)
