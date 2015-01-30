# This setup file configures the nicos daemon service.

description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    # to authenticate against the UserOffice, needs the "propdb" parameter
    # set on the Experiment object
    UserDB = device('frm2.proposaldb.Authenticator'),

    # fixed list of users:
    # first entry is the user name, second the hashed password, third the user level
    # (of course, for real passwords you don't calculate the hash here :)
    Auth   = device('services.daemon.auth.ListAuthenticator',
                    hashing = 'md5',
                    passwd = [('guest', '', 'guest'),
                              ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
                              ('admin', '21232f297a57a5a743894a0e4a801fc3', 'admin'),
                             ],
                   ),
    Daemon = device('services.daemon.NicosDaemon',
                    server = '',
                    authenticators = ['Auth', 'UserDB'],
                    loglevel = 'info',
                   ),
)
