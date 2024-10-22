description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'localhost'
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        alwayspoll = [],
        neverpoll = ['capacitance', 'ppms14', 'ppms9', 'matfun'],
        blacklist = ['adet', 'image', 'events', 'det'],
    ),
)
