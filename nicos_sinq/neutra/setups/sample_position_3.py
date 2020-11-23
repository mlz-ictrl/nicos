description = 'Sample position 3 motorization'

group = 'basic'

includes = ['camera_focus_3', 'beam_limiter_2', 'shutters', 'detector']

display_order = 50
epics_timeout = 3.0

devices = dict(
    sp3_tx = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = epics_timeout,
        description = 'Sample Position 3, Translation X',
        motorpv = 'SQ:NEUTRA:board1:SP3TX',
        errormsgpv = 'SQ:NEUTRA:board1:SP3TX-MsgTxt',
        precision = 0.01,
    ),
    sp3_ty_axis = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = epics_timeout,
        description = 'Sample Position 3, Translation Y Axis',
        motorpv = 'SQ:NEUTRA:board1:SP3TY',
        errormsgpv = 'SQ:NEUTRA:board1:SP3TY-MsgTxt',
        precision = 0.01,
        lowlevel = True,
    ),
    sp3_ty_brake = device('nicos.devices.epics.EpicsDigitalMoveable',
        epicstimeout = epics_timeout,
        description = 'Sample Position 3, Translation Y Brake',
        readpv = 'SQ:NEUTRA:b4io4:BrakeSP3',
        writepv = 'SQ:NEUTRA:b4io4:BrakeSP3',
        lowlevel = True,
    ),
    sp3_ty = device('nicos.devices.generic.sequence.LockedDevice',
        description = 'Sample Position 3, Translation Y',
        device = 'sp3_ty_axis',
        lock = 'sp3_ty_brake',
        unlockvalue = 1,
        lockvalue = 0,
        unit = 'mm',
    ),
    sp3_ry = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = epics_timeout,
        description = 'Sample Position 2, Rotation Y',
        motorpv = 'SQ:NEUTRA:board3:SP23RY',
        errormsgpv = 'SQ:NEUTRA:board3:SP23RY-MsgTxt',
        precision = 0.01,
        unit = 'deg',
    ),
    sp3_rz = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = epics_timeout,
        description = 'Sample Position 2, Rotation Z',
        motorpv = 'SQ:NEUTRA:board3:SP23RZ',
        errormsgpv = 'SQ:NEUTRA:board3:SP23RZ-MsgTxt',
        precision = 0.01,
        unit = 'deg',
    ),
)
