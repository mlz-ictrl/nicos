description = 'Collimator selector unit 1'

group = 'optional'

devices = dict(
    csu_1_motor=device('nicos.devices.generic.virtual.VirtualMotor',
        description='Motor changing guide position',
        fmtstr="%7.2f",
        userlimits=(-131.4, 0.),
        abslimits=(-131.4, 0.),
        curvalue=-5.1,
        unit='mm',
        speed=5.,
        lowlevel=True,
    ),
    coll_1_pos=device('nicos.devices.generic.Switcher',
        description='The collimator',
        moveable='csu_1_motor',
        mapping={
            'Position 1': -5.1,
            'Position 2': -61.25,
        },
        precision=0.05,
    ),
)
