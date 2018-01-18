description = 'Counter devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:mota:'

devices = dict(
    com=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Counter tilt motor',
               motorpv=pvprefix + 'com',
               errormsgpv=pvprefix + 'com-MsgTxt',
               ),
    coz=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Counter z translation motor',
               motorpv=pvprefix + 'coz',
               errormsgpv=pvprefix + 'coz-MsgTxt',
               ),
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
