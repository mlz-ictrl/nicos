description = 'Guide motors for small (!) movements for temperature drift compensation. Handle with care!'

display_order = 25

pvprefix = 'SQ:AMOR:mcu2:'

devices = dict(
    gd6 = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Guide motor axis 6',
        motorpv = pvprefix + 'gd6',
        errormsgpv = pvprefix + 'gd6-MsgTxt',
        can_disable = True,
        auto_enable = False,
        visibility = ('devlist', 'metadata', 'namespace'),
        requires = {'level': 'admin'},
    ),
)
