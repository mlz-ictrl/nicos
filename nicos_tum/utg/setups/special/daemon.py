description = 'setup for the execution daemon'

group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'sha1',
        # first entry is the user name, second the hashed password, third the
        # user level
        passwd = [('guest', '', 'guest'),
            ('user', '12dea96fec20593566ab75692c9949596833adc9', 'user'),
            ('admin', 'd033e22ae348aeb5660fc2140aec35850c4da997', 'admin')],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        authenticators = ['Auth'],
        loglevel = 'debug',
        server = '',
    ),
)
