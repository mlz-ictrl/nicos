description = 'For fixing the radial collimator'

devices = dict(
    cov = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Radial collimator',
        motorpv = 'SQ:ZEBRA:mcu1:COV',
        errormsgpv = 'SQ:ZEBRA:mcu1:COV-MsgTxt',
        precision = 0.5,
        can_disable = True,
    ),
)
