# This setup file configures the nicos daemon service.

description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        # the hashing maybe 'md5' or 'sha1'
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
