description = 'setup for the poller'
group = 'special'

includes = []

sysconfig = dict(
    cache = 'pumahw'
)

devices = dict(
    Poller = device('services.poller.Poller',
                    autosetup = True,
                    poll = ['lakeshore', 'detector', 'befilter'], # setups for which all devices are polled
                    alwayspoll = [],    # devices which are always polled
                    neverpoll = []),    # devices which are never polled
)
