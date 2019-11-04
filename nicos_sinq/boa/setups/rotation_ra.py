description='Rotation RA'

pvprefix='SQ:BOA:ra:'

devices = dict(
    ra=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='RA rotation',
               motorpv=pvprefix + 'RA',
               errormsgpv=pvprefix + 'RA-MsgTxt',
               ),
)
