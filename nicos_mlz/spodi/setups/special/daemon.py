description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    # to authenticate against the UserOffice, needs the "propdb" parameter
    # set on the Experiment object
    UserDB = device('nicos_mlz.devices.proposaldb.Authenticator'),

    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        # the hashing maybe 'md5' or 'sha1'
        hashing = 'md5',
        passwd = [('guest', '', 'guest'),
                  ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
                  ('admin', '04ec0deed0abb157dab3031b26b3db23', 'admin')],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['Auth'], # and/or 'UserDB'
        loglevel = 'info',
    ),
)
