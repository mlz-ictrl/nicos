description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth   = device('nicos.services.daemon.auth.list.Authenticator',
                    hashing = 'md5',
                    passwd = [
                       ('admin', 'd8d701b8fec19d1b19af2ec040806ad1', 'admin'),
                       ('guest', '084e0343a0486ff05530df6c705c8bb4', 'guest'),
                       ('user', '3fabfd016fd3f3310981387bb917c0f1', 'user'),
                             ],
                   ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
                    server = '',
                    authenticators = ['Auth'],
                    loglevel = 'info',
                   ),
)
