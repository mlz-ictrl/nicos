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
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['NemoAuth'],
        loglevel = 'info',
    ),
)
