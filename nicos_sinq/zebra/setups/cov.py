description = 'For fixing the radial collimator'

devices = dict(
    cov = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Radial collimator',
        motorpv = 'SQ:ZEBRA:turboPmac1:COV',
    ),
)
