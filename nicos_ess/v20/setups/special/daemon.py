description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    # to authenticate against the UserOffice, needs the "propdb" parameter
    # set on the Experiment object
    # UserDB = device('nicos_mlz.devices.proposaldb.Authenticator'),

    # fixed list of users:
    # first entry is the user name, second the hashed password, third the user
    # level
    # The user level are 'guest, 'user', and 'admin', ascending ordered in
    # respect to the rights
    # The entries for the password hashes are generated from randomized
    # passwords and not reproduceable, please don't forget to create new ones:
    # start python
    # >>> import hashlib
    # >>> hashlib.md5('password').hexdigest()
    # or
    # >>> hashlib.sha1('password').hexdigest()
    # depending on the hashing algorithm
    Auth   = device('nicos.services.daemon.auth.list.Authenticator',
                    # the hashing maybe 'md5' or 'sha1'
                    hashing = 'sha1',
                    passwd = [('guest', '5698b08399150da341866a25e24a86e75e6b824d', 'guest'),
                              ('user', '0d0d9cd4c8e8a5e2e41fc213b9583b8d57127f0b', 'user'),
                              ('admin', '16b240db2878a9b89fd2ad342195e50baef45564', 'admin'),
                             ],
                   ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
                    # 'localhost' will normally bind the daemon to the loopback
                    # device, therefore just clients on the same machine will be
                    # able to connect !
                    # '' will bind the daemon to all network interfaces in the
                    # machine
                    # If server is a hostname (official computer name) or an IP
                    # address the daemon service will be bound the the
                    # corresponding network interface.
                    server = '',
                    authenticators = ['Auth'], # and/or 'UserDB'
                    loglevel = 'info',
                   ),
)

# This is required because of the way threading works in pyepics.
# If omitted, there may be problems accessing PVs from multiple threads.
startupcode='''
import nicos.devices.epics
'''
