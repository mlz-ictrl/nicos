description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'refsansctrl01.refsans.frm2'
)

devices = dict(
    Poller = device('services.poller.Poller',
                    alwayspoll = [],
                    neverpoll = [],
                    blacklist = []),
)
