description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'pumadma.puma.frm2'
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        autosetup = True,
        # setups for which all devices are polled
        # poll = ['lakeshore', 'detector', 'befilter'],
        # setups which are always polled
        alwayspoll = [],
        # setups which are never polled
        neverpoll = [
            'motorbus10',
            'motorbus13',
        ],
    ),
)
