description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'localhost'
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
                    autosetup = False,  # important! do not poll everything
                    poll = ['reactor'],
                    alwayspoll = [],
                    blacklist = []),
)
