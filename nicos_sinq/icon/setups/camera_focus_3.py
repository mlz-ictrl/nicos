description = 'Camera focusing at position 3'

group = 'lowlevel'

display_order = 55

devices = dict(
    focus_maxi = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        description = 'Camera focus maxi box',
        motorpv = 'SQ:ICON:board5:CMAX',
        errormsgpv = 'SQ:ICON:board5:CMAX-MsgTxt',
    ),
)
