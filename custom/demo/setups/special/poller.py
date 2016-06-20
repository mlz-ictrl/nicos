description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'localhost'
)

devices = dict(
    Poller = device('services.poller.Poller',
                    alwayspoll = [],
                    neverpoll = ['detector'],
                    blacklist = ['adet', 'image', 'events', 'det'],
                   ),
)
