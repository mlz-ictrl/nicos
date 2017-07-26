description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    UserDB = device('nicos_mlz.frm2.devices.proposaldb.Authenticator'),

    Auth   = device('nicos.services.daemon.auth.ListAuthenticator',
                    hashing = 'md5',
                    passwd = [('guest', '', 'guest'),
                              ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
                              ('admin', '21232f297a57a5a743894a0e4a801fc3', 'admin'),
                             ],
                   ),

    # AuthLDAP = device('nicos.services.daemon.auth.LDAPAuthenticator',
    #                   server = 'phaidra.admin.frm2',
    #                   userbasedn = 'ou=People,dc=frm2,dc=de',
    #                   groupbasedn = 'ou=Group,dc=frm2,dc=de',
    #                   grouproles = {
    #                       'nectar' : 'admin',
    #                       'ictrl' : 'admin',
    #                   },
    #                  ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
                    server = '0.0.0.0',
                    #authenticators = ['AuthLDAP'],
                    authenticators = ['UserDB', 'Auth'],
                    loglevel = 'info',
                   ),
)
