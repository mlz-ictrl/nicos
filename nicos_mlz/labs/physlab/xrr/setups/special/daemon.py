description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    NemoAuth = device('nicos_mlz.devices.nemo.Authenticator',
        nemourl = 'https://supportlabs.mlz-garching.de',
        instrument = 23,
        aliases = {
            'bveltel': ('bveltel', 'admin', True),
        },
    ),
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
        authenticators = ['NemoAuth'],
        loglevel = 'info',
    ),
)
