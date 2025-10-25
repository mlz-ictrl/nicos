description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.Authenticator'),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = configdata('config_data.daemon_bind') + ':1302',
        simmode = True,
        authenticators = ['Auth'],
        loglevel = 'info',
    ),
)
