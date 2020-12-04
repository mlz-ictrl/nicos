description = 'Sample position 2 motorization'

group = 'basic'

includes = ['camera_focus_2', 'beam_limiter_2', 'shutters', 'detector']

display_order = 30

epics_timeout = 3.0

devices = dict(
    sp2_tx = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = epics_timeout,
        description = 'Sample Position 2, Translation X',
        motorpv = 'SQ:NEUTRA:board4:SP2TX',
        errormsgpv = 'SQ:NEUTRA:board4:SP2TX-MsgTxt',
        precision = 0.01,
    ),
    sp2_ty = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = epics_timeout,
        description = 'Sample Position 2, Translation Y',
        motorpv = 'SQ:NEUTRA:board4:SP2TY',
        errormsgpv = 'SQ:NEUTRA:board4:SP2TY-MsgTxt',
        precision = 0.01,
    ),
    sp2_tz = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = epics_timeout,
        description = 'Sample Position 2, Translation Z',
        motorpv = 'SQ:NEUTRA:board4:SP2TZ',
        errormsgpv = 'SQ:NEUTRA:board4:SP2TZ-MsgTxt',
        precision = 0.01,
    ),
    sp2_ry = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = epics_timeout,
        description = 'Sample Position 2, Rotation Y',
        motorpv = 'SQ:NEUTRA:board3:SP23RY',
        errormsgpv = 'SQ:NEUTRA:board3:SP23RY-MsgTxt',
        precision = 0.01,
        unit = 'deg',
    ),
    sp2_rz = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = epics_timeout,
        description = 'Sample Position 2, Rotation Z',
        motorpv = 'SQ:NEUTRA:board3:SP23RZ',
        errormsgpv = 'SQ:NEUTRA:board3:SP23RZ-MsgTxt',
        precision = 0.01,
        unit = 'deg',
    ),
)
