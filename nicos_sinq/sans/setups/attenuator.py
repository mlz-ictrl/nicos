description = 'Devices for the attenuator'

group = 'lowlevel'

devices = dict(
    attpos = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Attenuator motor',
        motorpv = 'SQ:SANS:turboPmac1:attpos',
    ),
    att = device('nicos.devices.generic.switcher.Switcher',
        description = 'Attenuator choice',
        moveable = 'attpos',
        mapping = {
            '0': 0,
            '1': 60,
            '2': 120,
            '3': 180,
            '4': 240,
            '5': 300
        },
        precision = 1,
    ),
)
