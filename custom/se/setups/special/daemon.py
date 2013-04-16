description = 'setup for the execution daemon'
group = 'special'

#import hashlib

devices = dict(
    Auth   = device('services.daemon.auth.Authenticator'),
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'localhost',
                    authenticators = ['Auth'],
                    loglevel = 'info',
                   ),
)
