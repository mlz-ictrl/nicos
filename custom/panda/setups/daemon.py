description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'localhost',
                    startupsetup = 'base',
                    loglevel = 'debug',
                    authenticator = None),
)
