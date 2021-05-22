description = 'Counter devices in the SINQ AMOR.'

group='lowlevel'

pvprefix = 'SQ:AMOR:mota:'

devices = dict(
    c3z=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Counter z position single counter motor',
               motorpv=pvprefix + 'c3z',
               errormsgpv=pvprefix + 'c3z-MsgTxt',
               ),
    cox=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Counter x translation motor',
               motorpv=pvprefix + 'cox',
               errormsgpv=pvprefix + 'cox-MsgTxt',
               ),
)
