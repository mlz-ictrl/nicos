description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'resedahw',
)

devices = dict(
    Poller = device('services.poller.Poller',
                    autosetup = True,
                    alwayspoll = ['motors', 'powersupply', 'temperature',
                                  'capacitance', 'atts_slits',
                                  'frequencies',
                                 ],
                    neverpoll = [],
                    blacklist = []),
)
