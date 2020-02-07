description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    # to authenticate against the UserOffice, needs the "propdb" parameter
    # set on the Experiment object
    # UserDB = device('nicos_mlz.devices.proposaldb.Authenticator'),
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        # the hashing maybe 'md5' or 'sha1'
        hashing = 'md5',
        passwd = [('guest', '', 'guest'),
                  ('user', 'd3bde5ce3e546626df42771c58986d4e', 'user'),
                  ('admin', 'f3309476bdb36550aa8fb90ae748c9cc', 'admin'),
                 ],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['Auth'], # and/or 'UserDB'
        loglevel = 'info',
    ),
)
