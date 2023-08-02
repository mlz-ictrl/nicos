description = 'Counter devices in the SINQ AMOR.'

group='lowlevel'

pvprefix = 'SQ:AMOR:mota:'

devices = dict(
    c3z=device('nicos.devices.epics.pyepics.motor.EpicsMotor',
               description='Counter z position single counter motor',
               motorpv=pvprefix + 'c3z',
               errormsgpv=pvprefix + 'c3z-MsgTxt',
               ),
    cox=device('nicos.devices.epics.pyepics.motor.EpicsMotor',
               description='Counter x translation motor',
               motorpv=pvprefix + 'cox',
               errormsgpv=pvprefix + 'cox-MsgTxt',
               ),
)
