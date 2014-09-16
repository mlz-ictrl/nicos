description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    UserDB = device('frm2.auth.Frm2Authenticator'),

    Auth   = device('services.daemon.auth.ListAuthenticator',
                    hashing = 'sha1',
                    passwd = [('guest', 'da39a3ee5e6b4b0d3255bfef95601890afd80709', 'guest'),
                              ('user', '12dea96fec20593566ab75692c9949596833adc9', 'user'),
                              ('admin', 'd033e22ae348aeb5660fc2140aec35850c4da997', 'admin')],
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
                    authenticators = ['Auth'],
                    loglevel = 'info',
                   ),
)
