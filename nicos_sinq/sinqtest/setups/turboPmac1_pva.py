description = 'TurboPMAC test motors'

pvprefix = 'SQ:SINQTEST:turboPmac1:'

devices = dict(
    lin1_tp_pva = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Linear motor 1',
        motorpv = pvprefix + 'lin1',
        visibility = ('devlist', 'metadata', 'namespace'),
        monitor = True,
    ),
    rot2_tp_pva = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Rotary motor 2',
        motorpv = pvprefix + 'rot2',
        visibility = ('devlist', 'metadata', 'namespace'),
        monitor = True,
    ),
)
