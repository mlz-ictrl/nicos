description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    experiment = None,
    instrument = None,
    datasinks = [],
    notifiers = [],
    cache = 'localhost',
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
                    autosetup = True,
                    alwayspoll = [],
                    neverpoll = [],
                    loglevel = 'info',
                    blacklist = [],
                   ),
)
