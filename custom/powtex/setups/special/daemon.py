# This setup file configures the nicos daemon service.

description = 'setup for the execution daemon'
group = 'special'

import hashlib

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
                              ('user', hashlib.md5(b'user').hexdigest(), 'user'),
                              ('jcns', hashlib.md5(b'jcns').hexdigest(), 'admin'),
                              ('admin', hashlib.md5(b'admin').hexdigest(), 'admin')],
                   ),
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'localhost',
                    authenticators = ['Auth'], # or ['Auth', 'UserDB']
                    loglevel = 'debug',
                   ),
)
