description = 'Slit 4 devices in the SINQ AMOR.'

display_order = 70

pvprefix = 'SQ:AMOR:mcu4:'

devices = dict(
    d4v = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 4 vertical opening',
        motorpv = pvprefix + 'd4v',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    d4h = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 4 horizontal opening',
        motorpv = pvprefix + 'd4h',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
)
