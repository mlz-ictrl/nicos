description = 'el734 test motors'

display_order = 27

pvprefix = 'SQ:SINQTEST:el734_1:'

devices = dict(
    lin1_el = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Linear motor 1',
        motorpv = pvprefix + 'lin1',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
)
