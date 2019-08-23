description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        description = 'Authentication device',
        hashing = 'md5',
        # first entry is the user name, second the hashed password, third the user level
        passwd = [
            ('guest', '', 'guest'),
            ('admin', '51b8e46e7a54e8033f0d7a3393305cdb', 'admin'),
            ('jcns', '51b8e46e7a54e8033f0d7a3393305cdb', 'admin'),
            ('aweber', '3219e862ecf3d51fa1895e053d0e96cd', 'admin'),
        ],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        description = 'Daemon, executing commands and scripts',
        server = '',
        authenticators = ['Auth'],
        loglevel = 'debug',
    ),
)
