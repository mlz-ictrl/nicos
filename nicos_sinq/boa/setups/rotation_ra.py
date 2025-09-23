description = 'Rotation RA'

pvprefix = 'SQ:BOA:ra:'

group = 'lowlevel'

devices = dict(
    ra = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'RA rotation',
        motorpv = pvprefix + 'RA',
        errormsgpv = pvprefix + 'RA-MsgTxt',
        precision = 0.000125
    ),
)
