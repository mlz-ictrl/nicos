description = 'Monitors'

group = 'lowlevel'

devices = dict(
    m1 = device('nicos.devices.generic.VirtualCounter',
        description = 'Beam monitor M1',
        fmtstr = '%d',
        type = 'monitor',
        # lowlevel = True,
    ),
    m2 = device('nicos.devices.generic.VirtualCounter',
        description = 'Beam monitor M2',
        fmtstr = '%d',
        type = 'monitor',
        # lowlevel = True,
        countrate = 500,
    ),
    m2pos = device('nicos.devices.generic.ManualSwitch',
        description = 'M2 position',
        states = ['in', 'out']
    ),
    m3 = device('nicos.devices.generic.VirtualCounter',
        description = 'Beam monitor M3',
        fmtstr = '%d',
        type = 'monitor',
        # lowlevel = True,
        countrate = 300,
    ),
)
