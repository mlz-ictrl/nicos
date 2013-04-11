description = 'setup for the execution daemon'
group = 'special'
import hashlib

devices = dict(
    Auth   = device('services.daemon.auth.ListAuthenticator',  # or 'frm2.auth.Frm2Authenticator'
                    # first entry is the user name, second the hashed password, third the user level
                    passwd = [('guest', '', 'guest'),
                              ('user', hashlib.sha1('user').hexdigest(), 'user'),
                              ('admin', hashlib.sha1('admin').hexdigest(), 'admin')],
	           ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
                    server = 'pumahw.puma.frm2',
                    startupsetup = 'puma',
                    authenticators = ['Auth'],
                    loglevel = 'debug',
                   ),
)
