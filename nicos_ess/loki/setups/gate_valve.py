description = 'Vacuum gate valve'

group = 'optional'

devices = dict(
    gv_motor=device('nicos.devices.generic.virtual.VirtualMotor',
        description='Motor changing guide position',
        fmtstr="%7.2f",
        userlimits=(-131.4, 0.),
        abslimits=(-131.4, 0.),
        curvalue=-5.1,
        unit='mm',
        speed=20.,
        lowlevel=True,
    ),
    gv_position=device('nicos.devices.generic.Switcher',
        description='The position of the gate valve',
        moveable='gv_motor',
        mapping={
           'Open': -5.1,
           'Closed': -61.25,
        },
        precision=0.05,
    ),
)
