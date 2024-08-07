description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = configdata('config_data.host'),
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        description = 'Device polling service',
        alwayspoll = [],
        neverpoll = [],
        blacklist = [],  # ['tas'],
    ),
)
