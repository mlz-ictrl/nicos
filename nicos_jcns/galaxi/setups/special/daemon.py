description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'md5',
        passwd = [
            ('guest', '', 'guest'),
            ('jcns', '51b8e46e7a54e8033f0d7a3393305cdb', 'admin'),
        ],
    ),
    LDAPAuth = device('nicos_jcns.devices.ldap.Authenticator',
        uri = 'ldap://iffldap.iff.kfa-juelich.de',
        userbasedn = 'ou=People,dc=iff,dc=kfa-juelich,dc=de',
        groupbasedn = 'ou=Groups,dc=iff,dc=kfa-juelich,dc=de',
        grouproles = {
            'ictrl': 'admin',
            'jcns-1': 'user',
            'jcns-2': 'user',
        },
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        description = 'Daemon, executing commands and scripts',
        server = '',
        authenticators = ['Auth', 'LDAPAuth'],
        loglevel = 'debug',
    ),
)
