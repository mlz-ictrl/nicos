description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    GhostAuth = device(
        'nicos_mlz.devices.ghost.Authenticator',
        description = 'GHoST proposal system authentication',
        instrument = 'VMOKE',
        ghosthost = 'ghost.k8s-test.frm2.tum.de',
    ),
    # fixed list of users:
    # first entry is the user name, second the hashed password, third the user level
    # (of course, for real passwords you don't calculate the hash here :)
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'md5',
        passwd = [('guest', '', 'guest'),
                  ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
                  ('admin', '21232f297a57a5a743894a0e4a801fc3', 'admin')],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['GhostAuth', 'Auth'],
        loglevel = 'info',
    ),
)
