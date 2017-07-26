description = 'setup for the daemon'
group = 'special'

devices = dict(
    Auth   = device('nicos.services.daemon.auth.Authenticator'),
    Daemon = device('nicos.services.daemon.NicosDaemon',
                    server = 'resictrl.resi.frm2',
                    loglevel = 'debug',
                    authenticators = ['Auth'],
                   ),
)
