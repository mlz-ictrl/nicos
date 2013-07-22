description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    experiment = None,
    instrument = None,
    datasinks = [],
    notifiers = [],
    cache = 'mira1',
)

devices = dict(
    Poller = device('services.poller.Poller',
                    autosetup = True,
                    alwayspoll = ['ubahn', 'memograph'],
                    neverpoll = ['mslit2'],
                    loglevel = 'info',
                    blacklist = ['psd']),
)
