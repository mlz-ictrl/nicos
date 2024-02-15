description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth=device('nicos.services.daemon.auth.list.Authenticator',
                # the hashing maybe 'md5' or 'sha1'
                hashing='sha1',
                passwd = configdata('config_sinq.passwds'),
                ),
    Daemon=device('nicos.services.daemon.NicosDaemon',
                  server='',
                  authenticators=['Auth', ],  # and/or 'UserDB'
                  loglevel='info',
                  ),
)

startupcode = '''
import nicos.devices.epics.pyepics
'''
