description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    GhostAuth = device('nicos_mlz.devices.ghost.Authenticator',
        description = 'GHoST proposal system authentication',
        instrument = 'KWS-3',
        ghosthost = 'ghost.mlz-garching.de',
        aliases = {
        },
    ),
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
         hashing = 'md5',
         passwd = [
             ('guest', '', 'guest'),
             ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
             ('jcns', '51b8e46e7a54e8033f0d7a3393305cdb', 'admin'),
         ],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['GhostAuth', 'Auth'],
        loglevel = 'info',
    ),
)
