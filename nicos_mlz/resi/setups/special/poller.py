description = 'setup for the poller'

group = 'special'

includes = []

sysconfig = dict(cache='resictrl.resi.frm2')

devices = dict(
    Poller=device('nicos.services.poller.Poller',
                  loglevel='info',
                  autosetup=True,
                  alwayspoll=['ls340', 'io', 'reactor', 'ubahn', 'outerworld',
                              'detector'],
                  neverpoll=['base', 'system', 'resi'],
                  blacklist=[],
                  ),
)
