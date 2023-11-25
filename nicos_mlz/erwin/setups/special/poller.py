description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'localhost'
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        alwayspoll = [],  # ['charmsmall'],
        neverpoll = ['detector', ],
        blacklist = ['adet', 'image', 'events', 'det'],
        loglevel = 'debug',
    ),
)
