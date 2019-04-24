description = 'setup for the poller'
group = 'special'

sysconfig = dict(cache = 'refsanssw.refsans.frm2')

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        alwayspoll = ['memograph'],
        neverpoll = ['qmesydaq'],
        blacklist = []
    ),
)
