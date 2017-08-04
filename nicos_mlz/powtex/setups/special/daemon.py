# This setup file configures the nicos daemon service.

description = 'setup for the execution daemon'
group = 'special'

import hashlib

devices = dict(
    # to authenticate against the UserOffice, needs the "propdb" parameter
    # set on the Experiment object
    UserDB = device('nicos_mlz.frm2.devices.proposaldb.Authenticator'),

    # fixed list of users:
    # first entry is the user name, second the hashed password, third the user level
    # (of course, for real passwords you don't calculate the hash here :)
    Auth   = device('nicos.services.daemon.auth.list.Authenticator',
                    hashing = 'md5',
                    passwd = [('guest', '', 'guest'),
                              ('user', hashlib.md5(b'user').hexdigest(), 'user'),
                              ('jcns', hashlib.md5(b'jcns').hexdigest(), 'admin'),
                              ('admin', hashlib.md5(b'admin').hexdigest(), 'admin')],
                   ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
                    server = 'localhost',
                    authenticators = ['Auth'], # or ['Auth', 'UserDB']
                    loglevel = 'debug',
                   ),
)
