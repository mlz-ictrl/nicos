description = 'setup for the poller'

group = 'special'

sysconfig = dict(
    cache = 'phys.panda.frm2'
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        loglevel = 'info',
        autosetup = True,
        alwayspoll = ['memograph'],
        neverpoll = ['blenden_old'],
        blacklist = [],
    ),
)
