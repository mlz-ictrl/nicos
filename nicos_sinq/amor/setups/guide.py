description = 'Guide motors for small (!) movements for temperature drift compensation. Handle with care!'

display_order = 25

pvprefix = 'SQ:AMOR:mcu2:'

devices = dict(
    gd6 = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Guide motor axis 6',
        motorpv = pvprefix + 'gd6',
        visibility = ('devlist', 'metadata', 'namespace'),
        requires = {'level': 'admin'},
    ),
)
