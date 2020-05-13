description = 'Beamstop related devices'

group = 'optional'

devices = dict(
    beamstop_mon=device('nicos.devices.generic.VirtualCounter',
        description='Beam monitor 5',
        fmtstr='%d',
        type='monitor',
        countrate=300,
    ),
    beamstop_motor=device('nicos.devices.generic.virtual.VirtualMotor',
        description='Motor for changing beamstop',
        fmtstr="%7.2f",
        userlimits=(0, 70),
        abslimits=(0, 70),
        curvalue=0,
        unit='mm',
        speed=10.,
        lowlevel=True,
    ),
    beamstop_size=device('nicos.devices.generic.Switcher',
        description='The current beamstop',
        moveable='beamstop_motor',
        mapping={
            '1 (XS)': 0,
            '2 (S)': 10,
            '3 (M)': 20,
            '4 (L)': 30,
            '5 (XL)': 40,
        },
        precision=0.05,
    ),
)
