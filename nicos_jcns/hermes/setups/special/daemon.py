description = 'setup for the HERMES execution daemon'
group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'md5',
        passwd = [('hermes', 'f1ae4a2a8b15cfb0ad8329e251967ab6', 'user'),
                  ('jcns', '51b8e46e7a54e8033f0d7a3393305cdb', 'admin')],
    ),
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = ['ldaps://ldaps.iff.kfa-juelich.de'],
        userbasedn = 'cn=users,cn=accounts,dc=iff,dc=kfa-juelich,dc=de',
        groupbasedn = 'cn=groups,cn=accounts,dc=iff,dc=kfa-juelich,dc=de',
        grouproles = {'ictrl': 'admin', 'jcns-all': 'user'},
        userroles = {'paulin': 'admin', 'ruecker': 'admin',
                     'zakalek': 'admin'},
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['Auth', 'LDAPAuth'],
    ),
)
