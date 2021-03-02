description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        # the hashing maybe 'md5' or 'sha1'
        hashing = 'md5',
        passwd = [('guest', '', 'guest'),
                  ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
                  ('admin', '04ec0deed0abb157dab3031b26b3db23', 'admin')],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['Auth'],
        loglevel = 'info',
    ),
)
