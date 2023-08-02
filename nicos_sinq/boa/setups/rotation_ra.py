description = 'Rotation RA'

pvprefix = 'SQ:BOA:ra:'

devices = dict(
    ra = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'RA rotation',
        motorpv = pvprefix + 'RA',
        errormsgpv = pvprefix + 'RA-MsgTxt',
    ),
)
