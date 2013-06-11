description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'localhost',
)

devices = dict(
    Poller = device('services.poller.Poller',
                    autosetup = True,
                    alwayspoll = ['startup', 'powersupply', 'temperature',
                                  'capacitance', 'attenuatorsSlits',
                                  'frequencies',
                                 ],
                    neverpoll = [],
                    blacklist = []),
)
