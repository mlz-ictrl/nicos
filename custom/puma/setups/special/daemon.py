description = 'setup for the execution daemon'
group = 'special'
import hashlib

devices = dict(
    UserDB = device('frm2.proposaldb.Authenticator'),
    Auth   = device('services.daemon.auth.ListAuthenticator',
                    # first entry is the user name, second the hashed password, third the user level
                    passwd = [('guest', '', 'guest'),
                              ('user', hashlib.sha1(b'user').hexdigest(), 'user'),
                              ('admin', hashlib.sha1(b'admin').hexdigest(), 'admin')],
                   ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
                    server = 'pumahw.puma.frm2',
                    authenticators = ['Auth'], # and/or 'UserDB'
                    loglevel = 'debug',
                   ),
)
