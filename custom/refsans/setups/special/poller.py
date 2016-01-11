description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'refsans10.refsans.frm2'
)

devices = dict(
    Poller = device('services.poller.Poller',
                    alwayspoll = [],
                    blacklist = []),
)
