description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'sha1',
        passwd = [
            ('spy', '15346b593c4d0cf05fb6e67a5669d852e6550481', 'guest'),
            ('user', '0c42722568e3d5471031c3be7d029f9b41123552', 'user'),
            ('admin', '76702e9ada292df094a875e5f72e9f778099d477', 'admin'),
            ('lnsadmin', '76702e9ada292df094a875e5f72e9f778099d477', 'admin')
        ],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = [
            'Auth',
        ],
        loglevel = 'debug',
    ),
)

startupcode = '''
import nicos.devices.epics
'''
