description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'pumahw.puma.frm2',
                    loglevel = 'info'),
)
