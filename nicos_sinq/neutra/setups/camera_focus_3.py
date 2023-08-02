description = 'Camera Focusing Maxibox'

pvprefix = 'SQ:NEUTRA:board1:'

group = 'lowlevel'

display_order = 60

devices = dict(
    focus_maxi = device('nicos.devices.epics.pyepics.motor.HomingProtectedEpicsMotor',
        description = 'Camera Focusing Maxibox',
        motorpv = pvprefix + 'CMAX',
        errormsgpv = pvprefix + 'CMAX-MsgTxt',
    ),
)
