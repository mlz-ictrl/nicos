description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'sha1',
        passwd = configdata('config_sinq.passwds') + [
            ('lnsadmin', '76702e9ada292df094a875e5f72e9f778099d477', 'admin'),
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
import nicos.devices.epics.pyepics
'''
