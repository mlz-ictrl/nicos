description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'cpci1.toftof.frm2'
)

devices = dict(
    Poller = device('services.poller.Poller',
                    autosetup = False,  # important! do not poll everything
                    poll = ['reactor'],
                    alwayspoll = [],
                    blacklist = []),
)
