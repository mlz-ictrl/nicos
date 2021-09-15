description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    # use only 'localhost' if the cache is really running on the same machine,
    # otherwise use the official computer name
    cache='localhost'
)

devices = dict(
    Poller=device('nicos.services.poller.Poller',
                  alwayspoll=[],
                  neverpoll=[],
                  blacklist=[],
                  loglevel='debug'
                  ),
)
