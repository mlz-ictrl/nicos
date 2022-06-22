description = 'setup for the TMR execution daemon'
group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'md5',
        passwd = [('tmr', '49db39a94421021f8568b5bb5712dd92', 'user'),
                  ('jcns', '51b8e46e7a54e8033f0d7a3393305cdb', 'admin')],
    ),
    LDAPAuth=device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = ['ldaps://ldaps.iff.kfa-juelich.de'],
        userbasedn = 'cn=users,cn=accounts,dc=iff,dc=kfa-juelich,dc=de',
        groupbasedn = 'cn=groups,cn=accounts,dc=iff,dc=kfa-juelich,dc=de',
        grouproles = {'ictrl': 'admin', 'jcns-all': 'user'},
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['Auth', 'LDAPAuth'],
    ),
)
