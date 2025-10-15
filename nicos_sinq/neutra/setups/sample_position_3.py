description = 'Sample position 3 motorization'

display_order = 30

pvprefix = 'SQ:NEUTRA:turboPmacSample:'
devices = dict(
    sp3_tx = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample Position 3, Translation X',
        motorpv = pvprefix + 'sp3_tx',
    ),
    sp3_ty = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample Position 3, Translation Y',
        motorpv = pvprefix + 'sp3_ty',
    ),
)
