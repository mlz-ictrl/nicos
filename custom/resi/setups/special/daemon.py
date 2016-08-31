description = 'setup for the daemon'
group = 'special'

devices = dict(
    Auth   = device('services.daemon.auth.Authenticator'),
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'resictrl.resi.frm2',
                    loglevel = 'debug',
                    authenticators = ['Auth'],
                   ),
)
