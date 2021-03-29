description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    GhostAuth = device('nicos_mlz.devices.ghost.Authenticator',
        description = 'GHoST proposal system authentication',
        instrument = 'PANDA',
        ghosthost = 'ghost.mlz-garching.de',
        aliases = {
        },
    ),
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        description = 'Authentication device',
        hashing = 'md5',
        # first entry is the user name, second the hashed password, third the user level
        passwd = [
            ('guest', '', 'guest'),
            ('panda', 'c2d577632fcc652244dd3ae0b2a0d819', 'user'),
            ('admin', '51b8e46e7a54e8033f0d7a3393305cdb', 'admin'),
            ('jcns', '51b8e46e7a54e8033f0d7a3393305cdb', 'admin'),
            ('astrid', '54709903e06a8be9a62a649cc8ec2f1d', 'admin'),
            ('aweber', '3219e862ecf3d51fa1895e053d0e96cd', 'admin'),
            ('cfranz', '54709903e06a8be9a62a649cc8ec2f1d', 'admin'),
            ('alistair', '54709903e06a8be9a62a649cc8ec2f1d', 'admin'),
        ],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        description = 'Daemon, executing commands and scripts',
        server = '',
        authenticators = ['GhostAuth', 'Auth'],
        loglevel = 'info',
    ),
)
