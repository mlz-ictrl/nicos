description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'localhost'
)

devices = dict(
    Poller = device('services.poller.Poller',
                    alwayspoll = [],
                    neverpoll = ['detector', 'image', 'events', 'adet', ],
                    blacklist = [],
                   ),
)
