description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    NemoAuth = device('nicos_mlz.devices.nemo.Authenticator',
        nemourl = 'https://supportlabs.mlz-garching.de',
        instrument = 24,
        aliases = {
            'bveltel': ('bveltel', 'admin', True),
        },
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = 'localhost',
        authenticators = ['NemoAuth'],
        loglevel = 'info',
    ),
)
