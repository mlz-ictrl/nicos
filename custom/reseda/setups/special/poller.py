description = 'setup for the poller'
group = 'special'

sysconfig = dict(cache = 'resedahw2.reseda.frm2',)

devices = dict(
    Poller = device('services.poller.Poller',
        autosetup = True,
        alwayspoll = [
        ],
        neverpoll = [],
        blacklist = []
    ),
)
