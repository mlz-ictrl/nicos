description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'localhost',
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        autosetup = True,
        alwayspoll = [],
        neverpoll = [],
        blacklist = [
            'scandet',
        ],
    ),
)
