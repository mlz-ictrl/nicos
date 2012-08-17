description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Daemon = device('nicos.daemon.NicosDaemon',
                    server = 'pumahw.puma.frm2',
                    loglevel = 'info'),
)
