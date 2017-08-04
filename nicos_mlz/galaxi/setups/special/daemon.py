# This setup file configures the nicos daemon service.

description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    # fixed list of users:
    # first entry is the user name, second the hashed password, third the user level
    # (of course, for real passwords you don't calculate the hash here :)
    Auth   = device('nicos.services.daemon.auth.list.Authenticator',
                    hashing = 'md5',
                    passwd = [('guest', '', 'guest'),
                              ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
                              ('jcns', 'bddb0acb705429fc46713aec4613b2cb', 'admin'),
                              ('admin', '21232f297a57a5a743894a0e4a801fc3', 'admin'),
                             ],
                   ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
                    server = 'localhost',
                    authenticators = ['Auth'],
                    loglevel = 'debug',
                   ),
)
