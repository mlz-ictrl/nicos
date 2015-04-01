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
                    alwayspoll = ['ubahn', 'meteo', 'memograph', 'radmon'],
                    neverpoll = ['gaussmeter'],
                    loglevel = 'info',
                    blacklist = ['psd']),
)
