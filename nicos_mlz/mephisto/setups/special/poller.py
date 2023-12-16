description = 'setup for the poller'
group = 'special'

sysconfig = dict(cache = 'mephisto17.office.frm2.tum.de')

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        alwayspoll = ['tube_environ', 'pressure'],
        blacklist = ['tas']
    ),
)
