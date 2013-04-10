description = 'setup for the daemon'
group = 'special'

devices = dict(
    Auth   = device('services.daemon.auth.Authenticator'),
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'resi1',
                    startupsetup = 'base',
                    loglevel = 'debug',
                    authenticators = ['Auth'],
                   ),
)
