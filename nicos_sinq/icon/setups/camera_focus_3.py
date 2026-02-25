description = 'Camera focusing at position 3'

group = 'lowlevel'

display_order = 55

devices = dict(
    focus_maxi = device('nicos_sinq.icon.devices.iconmotor.HomingProtectedEpicsMotor',
        description = 'Camera focus maxi box',
        motorpv = 'SQ:ICON:board5:CMAX',
        errormsgpv = 'SQ:ICON:board5:CMAX-MsgTxt',
        precision = 0.001,
    ),
)
