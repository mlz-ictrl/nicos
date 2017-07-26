description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth   = device('nicos.services.daemon.auth.Authenticator'),
    Daemon = device('nicos.services.daemon.NicosDaemon',
                    server = 'localhost',
                    authenticators = ['Auth'],
                    loglevel = 'info',
                   ),
)
