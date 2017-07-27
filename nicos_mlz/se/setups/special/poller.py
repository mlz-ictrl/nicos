description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'sehw.se.frm2'
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
                    autosetup = True,
                    poll = [],
                    alwayspoll = [],
                    blacklist = []),
)
