description = 'setup for the daemon'
group = 'special'

devices = dict(
    Auth   = device('nicos.services.daemon.auth.list.Authenticator',
                    hashing = 'md5',
                    passwd = [('admin', 'cf5bdfb40421ac1f30cc4d45b66b5a81', 'admin'),
                              ('', '', 'user')]),
    Daemon = device('nicos.services.daemon.NicosDaemon',
                    server = 'mira1:1302',
                    loglevel = 'info',
                    simmode = True,
                    authenticators = ['Auth']),
)
