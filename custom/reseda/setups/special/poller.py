description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'resedahw2',
)

devices = dict(
    Poller = device('services.poller.Poller',
                    autosetup = True,
                    alwayspoll = ['motors', 'powersupply', 'temperature',
                                  'atts_slits',
                                  'frequencies',
                                 ],
                    neverpoll = ['capacitance'],
                    blacklist = ['Sel', 'Lambda']),
)
