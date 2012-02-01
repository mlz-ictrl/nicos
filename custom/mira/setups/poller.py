description = 'setup for the poller'
group = 'special'

includes = ['all_devices']

sysconfig = dict(
    experiment = None,
    instrument = None,
    datasinks = [],
    notifiers = [],
)

devices = dict(
    Poller = device('nicos.poller.Poller',
                    autosetup = True,
                    alwayspoll = [],
                    loglevel = 'info',
                    blacklist = ['psd']),
)
