description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = configdata('config_data.cache_host'),
)

devices = dict(
   Poller = device('nicos.services.poller.Poller',
        alwayspoll = ['collimation', 'pressure',
                      'astrium',
                      'detector',
                      'reactor', 'selector_tower',
                      'guidehall', 'nl4a', 'memograph',
                      'outerworld', 'ieee',
        ],
        blacklist = [],
   ),
)
