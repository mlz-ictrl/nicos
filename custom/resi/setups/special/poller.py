description = 'setup for the poller'

group = 'special'

includes = []

sysconfig = dict(cache='localhost')

devices = dict(
    Poller=device('services.poller.Poller',
                  loglevel='info',
                  autosetup=True,
                  alwayspoll=['ls340', 'io', 'reactor', 'ubahn', 'outerworld',
                              'detector'],
                  neverpoll=['base', 'system', 'resi'],
                  blacklist=[],
                  ),
)
