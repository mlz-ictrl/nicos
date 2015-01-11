description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    UserDB = device('frm2.proposaldb.Authenticator'),

    Auth   = device('services.daemon.auth.ListAuthenticator',
                    hashing = 'md5',
                    passwd = [('guest', '084e0343a0486ff05530df6c705c8bb4', 'guest'),
                              ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
                              ('admin', '21232f297a57a5a743894a0e4a801fc3', 'admin')],
                   ),

    #AuthLDAP   = device('services.daemon.auth.LDAPAuthenticator',
    #                server = 'phaidra.admin.frm2',
    #                userbasedn = 'ou=People,dc=frm2,dc=de',
    #                groupbasedn = 'ou=Group,dc=frm2,dc=de',
    #                grouproles = {
    #                    'nectar' : 'admin',
    #                    'ictrl' : 'admin',
    #                },
    #               ),
    Daemon = device('services.daemon.NicosDaemon',
                    server = '0.0.0.0',
                    #authenticators = ['AuthLDAP'],
                    authenticators = ['UserDB', 'Auth'],
                    loglevel = 'info',
                   ),
)
