description = 'Devices for the attenuator'

devices = dict(
    attpos = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Attenuator motor',
        motorpv = 'SQ:SANS:mcu1:attpos',
        errormsgpv = 'SQ:SANS:mcu1:attpos' + '-MsgTxt',
        precision = 0.1,
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
