description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    NemoAuth = device('nicos_mlz.devices.nemo.Authenticator',
        nemourl = 'https://physicslab.frm2.tum.de',
        instrument = 24,
        aliases = {
            'bveltel': ('bveltel', 'admin', True),
        },
    ),
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'md5',
        # for the meaning of these entries see
        # https://forge.frm2.tum.de/nicos/doc/nicos-stable/services/daemon/#nicos.services.daemon.auth.list.Authenticator
        passwd = [
            ('guest', '', 'guest'),
            # The entries for these password hashes are generated from randomized
            # passwords and not reproduceable, please don't forget to create new
            # ones.
            ('user', 'd3bde5ce3e546626df42771c58986d4e', 'user'),
            ('admin', 'f3309476bdb36550aa8fb90ae748c9cc', 'admin'),
        ],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = 'localhost',
        authenticators = ['NemoAuth'], # 'Auth'],
        loglevel = 'info',
    ),
)
