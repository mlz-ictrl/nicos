description = 'setup for the poller'

group = 'special'

sysconfig = dict(
    cache = 'tofhw.toftof.frm2'
)

devices = dict(
    Poller = device('services.poller.Poller',
                    autosetup = True,
                    poll = [],
                    neverpoll = ['detector', 'measurement', 'notifiers'],
                    alwayspoll = ['reactor'],
                    blacklist = []),
)
