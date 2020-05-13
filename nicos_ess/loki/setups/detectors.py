description = 'Detectors'

group = 'optional'

devices = dict(
    bank_3_motor=device('nicos.devices.generic.virtual.VirtualMotor',
        description='x position of detector bank 3',
        fmtstr="%7.2f",
        userlimits=(-100, 100),
        abslimits=(-100, 100),
        curvalue=0,
        unit='cm',
        speed=5.,
    ),
)
