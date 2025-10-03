description = 'Rotation RF'

pvprefix = 'SQ:BOA:turboPmac2:'

devices = dict(
    rf = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'RR rotation',
        motorpv = pvprefix + 'RF',
    ),
)
