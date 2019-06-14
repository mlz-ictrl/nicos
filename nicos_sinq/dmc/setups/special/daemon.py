description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth=device('nicos.services.daemon.auth.list.Authenticator',
                hashing='sha1',
                passwd=[('spy', '15346b593c4d0cf05fb6e67a5669d852e6550481',
                         'guest'),
                        ('user', '27762722c263f0244de1116edd70cd4703695d03',
                         'user'),
                        ('admin', '76702e9ada292df094a875e5f72e9f778099d477',
                         'admin'),
                        ],
                ),
    Daemon=device('nicos.services.daemon.NicosDaemon',
                  server='',
                  authenticators=['Auth', ],
                  loglevel='info',
                  ),
)

startupcode = '''
import nicos.devices.epics
'''
