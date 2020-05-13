description = 'Monitors'

group = 'optional'

devices = dict(
    mon_1=device('nicos.devices.generic.VirtualCounter',
        description='Beam monitor 1',
        fmtstr='%d',
        type='monitor',
    ),
    mon_2=device('nicos.devices.generic.VirtualCounter',
        description='Beam monitor 2',
        fmtstr='%d',
        type='monitor',
        countrate=500,
    ),
    mon_3=device('nicos.devices.generic.VirtualCounter',
        description='Beam monitor 3',
        fmtstr='%d',
        type='monitor',
        countrate=300,
    ),
    mon_4=device('nicos.devices.generic.VirtualCounter',
        description='Beam monitor 4',
        fmtstr='%d',
        type='monitor',
        countrate=500,
    ),
)
