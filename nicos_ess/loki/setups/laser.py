description = 'Laser alignment'

group = 'optional'

devices = dict(
    laser_z=device('nicos.devices.generic.virtual.VirtualMotor',
        description='Motor changing guide position',
        fmtstr="%7.2f",
        userlimits=(-100, 100),
        abslimits=(-100, 100),
        curvalue=0,
        unit='mm',
        speed=5.,
    ),
)
