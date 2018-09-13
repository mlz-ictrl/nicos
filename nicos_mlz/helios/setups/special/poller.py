description = 'setup for the poller'
group = 'special'

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        autosetup = True,
        alwayspoll = [],
        neverpoll = [],
        loglevel = 'info',
        blacklist = [],
    ),
)
