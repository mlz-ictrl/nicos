description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    # The entries for the password hashes are generated from randomized
    # passwords and not reproduceable, please don't forget to create new ones.
    # see https://forge.frm2.tum.de/nicos/doc/nicos-stable/services/daemon/#nicos.services.daemon.auth.list.Authenticator
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'md5',
        passwd = [
            ('guest', '', 'guest'),
            ('user', 'd3bde5ce3e546626df42771c58986d4e', 'user'),
            ('admin', 'f3309476bdb36550aa8fb90ae748c9cc', 'admin'),
        ],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['Auth'],
        loglevel = 'info',
    ),
)
