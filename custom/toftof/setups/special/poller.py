description = 'setup for the poller'

group = 'special'

sysconfig = dict(
    cache = 'tofhw.toftof.frm2'
)

devices = dict(
    Poller = device('services.poller.Poller',
                    autosetup = False,  # important! do not poll everything
                    poll = ['chopper', 'reactor', 'vacuum', 'voltage', 'table'] +
                           ['slit', 'safety', 'system', 'collimator', 'ng'] +
                           ['he3', 'htf', 'ls', 'biofurnace', 'cryo_ccr'] +
                           ['pressure', 'ccr17', 'chmemograph', 'lascon',],
                    alwayspoll = [],
                    blacklist = []),
)
