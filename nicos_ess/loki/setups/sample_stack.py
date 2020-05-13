description = 'Sample positioning stack'

group = 'optional'

devices = dict(
    stack_x=device('nicos.devices.generic.virtual.VirtualMotor',
        description='Motor for x axis',
        fmtstr="%7.2f",
        userlimits=(-100, 100),
        abslimits=(-100, 100),
        curvalue=0,
        unit='mm',
        speed=5.,
    ),
    stack_y=device('nicos.devices.generic.virtual.VirtualMotor',
        description='Motor for y axis',
        fmtstr="%7.2f",
        userlimits=(-100, 100),
        abslimits=(-100, 100),
        curvalue=0,
        unit='mm',
        speed=5.,
    ),
    stack_z=device('nicos.devices.generic.virtual.VirtualMotor',
        description='Motor for z axis',
        fmtstr="%7.2f",
        userlimits=(-100, 100),
        abslimits=(-100, 100),
        curvalue=0,
        unit='mm',
        speed=5.,
    ),
)
