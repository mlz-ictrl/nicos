description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'sha1',
        passwd = [
            # ('guest', 'da39a3ee5e6b4b0d3255bfef95601890afd80709', 'guest'),
            ('guest', '', 'guest'),
            ('user', '12dea96fec20593566ab75692c9949596833adc9', 'user'),
            ('admin', 'd033e22ae348aeb5660fc2140aec35850c4da997', 'admin'),
        ],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '0.0.0.0',
        authenticators = ['Auth', ],
    ),
)

startupcode = '''
import nicos.devices.epics.pyepics
'''
