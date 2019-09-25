description = 'setup for the poller'
group = 'special'

sysconfig = dict(cache = 'refsansctrl01.refsans.frm2.tum.de')

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        alwayspoll = ['memograph'],
        neverpoll = ['qmesydaq'],
        blacklist = []
    ),
)
