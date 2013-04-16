description = 'setup for the execution daemon'

group = 'special'

devices = dict(
    Auth   = device('services.daemon.auth.Authenticator'),
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'localhost',
                    loglevel = 'debug',
                    authenticators = ['Auth'],
                   ),
)
