description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    # to authenticate against the UserOffice, needs the "propdb" parameter
    # set on the Experiment object
    UserDB = device('nicos_mlz.devices.proposaldb.Authenticator'),

    Auth   = device('nicos.services.daemon.auth.list.Authenticator',
                    # the hashing maybe 'md5' or 'sha1'
                    hashing = 'md5',
                    passwd = [('guest', '', 'guest'),
                             ],
                   ),
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = 'ldap://phaidra.admin.frm2',
        userbasedn = 'ou=People,dc=frm2,dc=de',
        groupbasedn = 'ou=Group,dc=frm2,dc=de',
        grouproles = {
            'stressi': 'admin',
            'ictrl': 'admin',
        }
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['LDAPAuth', 'Auth'], # and/or 'UserDB'
        loglevel = 'info',
    ),
)
