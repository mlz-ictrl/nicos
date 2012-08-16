description = 'setup for the poller'
group = 'special'

includes = []

sysconfig = dict(
    cache = 'pumahw'
)

devices = dict(
    Poller = device('nicos.poller.Poller',
                    autosetup = False,
                    poll = ['lakeshore', 'detector', 'befilter'],
                    alwayspoll = [],
                    neverpoll = []),
)
