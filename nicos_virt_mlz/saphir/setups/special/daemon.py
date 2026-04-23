description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'sha1',
        # for the meaning of these entries see
        # https://forge.frm2.tum.de/nicos/doc/nicos-stable/services/daemon/#nicos.services.daemon.auth.list.Authenticator
        passwd = [
            ('guest', '', 'guest'),
            ('user', '12dea96fec20593566ab75692c9949596833adc9', 'user'),
            ('admin', 'd033e22ae348aeb5660fc2140aec35850c4da997', 'admin'),
        ],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['Auth'],
        loglevel = 'info',
    ),
)
