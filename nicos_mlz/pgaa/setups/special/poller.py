description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'tequila.pgaa.frm2'
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        alwayspoll = ['pressure', 'pilz'],
        neverpoll = ['detector'],
        blacklist = [],
    ),
)
