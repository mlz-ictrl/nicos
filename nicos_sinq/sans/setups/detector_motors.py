description = 'Motors for the Detector'

group = 'lowlevel'
pvprefix = 'SQ:SANS:motb:'
devices = dict(
    detx = device('nicos_sinq.devices.epics.motor_deprecated.AbsoluteEpicsMotor',
        description = 'Detector X Translation',
        motorpv = pvprefix + 'detX',
        errormsgpv = pvprefix + 'detX-MsgTxt',
        precision = 0.5,
    ),
    dety = device('nicos_sinq.devices.epics.motor_deprecated.AbsoluteEpicsMotor',
        description = 'Detector Y Translation',
        motorpv = pvprefix + 'detY',
        errormsgpv = pvprefix + 'detY-MsgTxt',
        precision = 0.2,
    ),
    detphi = device('nicos_sinq.devices.epics.motor_deprecated.AbsoluteEpicsMotor',
        description = 'Detector Rotation',
        motorpv = pvprefix + 'phi',
        errormsgpv = pvprefix + 'phi-MsgTxt',
        precision = 0.2,
    ),
)
