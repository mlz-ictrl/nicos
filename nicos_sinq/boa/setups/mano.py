description = 'Mano Danalakshmi setup'

devices = dict(
    sam_x = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'x translation',
        motorpv = 'SQ:ICON:mano:SAM_X',
        errormsgpv = 'SQ:ICON:mano:SAM_X-MsgTxt',
        precision = 0.01,
    ),
    sam_y = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'y translation',
        motorpv = 'SQ:ICON:mano:SAM_Y',
        errormsgpv = 'SQ:ICON:mano:SAM_Y-MsgTxt',
        precision = 0.01,
    ),
)
