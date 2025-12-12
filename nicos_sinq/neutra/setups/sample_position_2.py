description = 'Sample position 2 motorization'

display_order = 30

pvprefix = 'SQ:NEUTRA:turboPmacSample:'
devices = dict(
    sp2_tx = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Sample Position 2, Translation X',
        motorpv = pvprefix + 'sp2_tx',
    ),
    sp2_ty = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Sample Position 2, Translation Y',
        motorpv = pvprefix + 'sp2_ty',
    ),
    sp2_tz = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Sample Position 2, Translation Z',
        motorpv = pvprefix + 'sp2_tz',
    ),
)
