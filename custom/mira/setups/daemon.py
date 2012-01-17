description = 'setup for the daemon'
group = 'special'

devices = dict(
    Daemon = device('nicos.daemon.NicosDaemon',
                    server = 'mira1',
                    startupsetup = 'base',
                    loglevel = 'debug'),
)
