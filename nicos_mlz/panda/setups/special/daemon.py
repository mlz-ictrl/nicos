description = 'setup for the execution daemon'
group = 'special'


devices = dict(
    UserDBAuth = device('nicos_mlz.frm2.devices.proposaldb.Authenticator'),
    Auth       = device('nicos.services.daemon.auth.ListAuthenticator',
                        description = 'Authentication device',
                        hashing = 'md5',
                        # first entry is the user name, second the hashed password, third the user level
                        passwd = [('guest', '', 'guest'),
                                  ('panda', '74a499fdf9c679c32549fc0d095cae75', 'user'),
                                  ('admin', '51b8e46e7a54e8033f0d7a3393305cdb', 'admin'),
                                  ('astrid', '54709903e06a8be9a62a649cc8ec2f1d', 'admin'),
                                  ('alex', '54709903e06a8be9a62a649cc8ec2f1d', 'admin'),
                                  ('andy', '54709903e06a8be9a62a649cc8ec2f1d', 'admin'),
                                  ('aweber', '3219e862ecf3d51fa1895e053d0e96cd', 'admin'),
                                  ('petr', '54709903e06a8be9a62a649cc8ec2f1d', 'admin')],
                       ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
                    description = 'Daemon, executing commands and scripts',
                    server = '',
                    authenticators = ['Auth', 'UserDBAuth'],
                    loglevel = 'debug',
                   ),
)
