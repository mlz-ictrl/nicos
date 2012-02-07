description = 'setup for the poller'
group = 'special'

includes = []

sysconfig = dict(
    cache = 'pandasrv'
)

devices = dict(
    Poller = device('nicos.poller.Poller',
                    autosetup = False,
                    poll = ['lakeshore', 'detector'],
                    alwayspoll = [],
                    neverpoll = []),
)
