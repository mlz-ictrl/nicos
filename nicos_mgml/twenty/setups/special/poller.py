description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = '20t.mgml:14869'
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        alwayspoll = [],
        neverpoll = ['detector', 'delta'],
        blacklist = ['adet', 'image', 'events', 'det'],
    ),
)
