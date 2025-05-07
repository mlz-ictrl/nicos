description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    # fixed list of users:
    # first entry is the user name, second the hashed password, third the user
    # level
    # The user level are 'guest, 'user', and 'admin', ascending ordered in
    # respect to the rights
    # The entries for the password hashes are generated from randomized
    # passwords and not reproducible, please don't forget to create new ones:
    # start python
    # >>> import hashlib
    # >>> hashlib.md5('password').hexdigest()
    # or
    # >>> hashlib.sha1('password').hexdigest()
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
