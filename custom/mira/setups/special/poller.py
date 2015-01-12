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
                    neverpoll = ['mslit2', 'gaussmeter', 'mslit1', 'gslits'],
                    loglevel = 'info',
                    blacklist = ['psd']),
)
