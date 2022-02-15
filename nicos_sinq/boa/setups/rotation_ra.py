description = 'Rotation RA'

pvprefix = 'SQ:BOA:ra:'

devices = dict(
    ra = device('nicos_ess.devices.epics.motor.EpicsMotor',
        description = 'RA rotation',
        motorpv = pvprefix + 'RA',
        errormsgpv = pvprefix + 'RA-MsgTxt',
    ),
)
