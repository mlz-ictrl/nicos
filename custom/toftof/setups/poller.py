description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'cpci1.toftof.frm2'
)

devices = dict(
    Poller = device('nicos.poller.Poller',
                    poll = ['chopper', 'power', 'vacuum', 'voltage'] +
                           ['he3', 'htf', 'ls', 'biofurnace'],
                    alwayspoll = [],
                    blacklist = []),
)
