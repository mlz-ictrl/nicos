description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    experiment = None,
    instrument = None,
    datasinks = [],
    notifiers = [],
    cache = 'deldaq50.del.frm2',
)

devices = dict(
    Poller = device('services.poller.Poller',
                    autosetup = True,
                    alwayspoll = [],
                    neverpoll = [],
                    loglevel = 'info',
                    blacklist = [],
                   ),
)

