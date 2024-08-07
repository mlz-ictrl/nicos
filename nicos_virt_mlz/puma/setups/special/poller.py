description = 'setup for the poller'

group = 'special'

sysconfig = dict(
    cache = configdata('config_data.host'),
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        alwayspoll = [],
        neverpoll = ['detector'],
        blacklist = ['image', 'events', 'det'],
    ),
)
