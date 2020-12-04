description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth=device('nicos.services.daemon.auth.list.Authenticator',
                # the hashing maybe 'md5' or 'sha1'
                hashing='sha1',
                passwd=[('spy', '15346b593c4d0cf05fb6e67a5669d852e6550481',
                         'guest'),
                        ('user', '21fb8406e5f81c24d4a5f5c7dd356e70a7288dc9',
                         'user'),
                        ('admin', '76702e9ada292df094a875e5f72e9f778099d477',
                         'admin'),
                        ],
                ),
    Daemon=device('nicos.services.daemon.NicosDaemon',
                  server='',
                  authenticators=['Auth', ],  # and/or 'UserDB'
                  loglevel='info',
                  ),
)

startupcode = '''
import nicos.devices.epics
'''
