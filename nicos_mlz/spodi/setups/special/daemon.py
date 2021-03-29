description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        # the hashing maybe 'md5' or 'sha1'
        hashing = 'md5',
        passwd = [('guest', '', 'guest'),
                  # ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
                  # ('admin', '04ec0deed0abb157dab3031b26b3db23', 'admin')
                 ],
    ),
    UserDBAuth = device('nicos_mlz.devices.ghost.Authenticator',
         description = 'FRM II user office authentication',
         instrument = 'SPODI',
         ghosthost = 'ghost.mlz-garching.de',
         aliases = {
         },
         loglevel = 'info',
    ),
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = 'ldap://phaidra.admin.frm2',
        userbasedn = 'ou=People,dc=frm2,dc=de',
        groupbasedn = 'ou=Group,dc=frm2,dc=de',
        grouproles = {
            'spodi': 'admin',
            'ictrl': 'admin',
            'se': 'user',
        }
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['UserDBAuth', 'LDAPAuth', 'Auth'],
        loglevel = 'info',
    ),
)
