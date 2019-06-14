description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth   = device('nicos.services.daemon.auth.list.Authenticator',
                    hashing = 'sha1',
                    passwd = [('guest', '5698b08399150da341866a25e24a86e75e6b824d', 'guest'),
                              ('user', '0d0d9cd4c8e8a5e2e41fc213b9583b8d57127f0b', 'user'),
                              ('admin', '16b240db2878a9b89fd2ad342195e50baef45564', 'admin'),
                             ],
                   ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
                    server = '',
                    authenticators = ['Auth'],
                    loglevel = 'info',
                   ),
)

# This is required because of the way threading works in pyepics.
# If omitted, there may be problems accessing PVs from multiple threads.
startupcode='''
import nicos.devices.epics
'''
