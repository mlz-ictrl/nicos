description = 'setup for the execution daemon'
group = 'special'
import hashlib


devices = dict(
    UserDBAuth = device('frm2.auth.Frm2Authenticator'),
    Auth       = device('services.daemon.auth.ListAuthenticator',
                         description = 'Authentication device',
                         hashing = 'md5',
                         # first entry is the user name, second the hashed password, third the user level
                         passwd = [('guest', '', 'guest'),
                                   ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
                                   ('admin', '21232f297a57a5a743894a0e4a801fc3', 'admin')],
                   ),
    Daemon = device('services.daemon.NicosDaemon',
                    description = 'Daemon, executing commands and scripts',
                    server = 'panda4.panda.frm2',
                    authenticators = ['UserDBAuth','Auth',],
                    loglevel = 'debug',
                    ),
)
