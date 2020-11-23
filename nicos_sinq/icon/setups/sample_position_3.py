description = 'Sample position 3 devices in the SINQ ICON.'

group = 'basic'

includes = [
    'neutron_aperture', 'shutters', 'beam_limiter_1', 'beam_limiter_2',
    'camera_focus_3', 'detector', 'sensors'
]

display_order = 50

devices = dict(
    sp3_allowed = device('nicos.devices.epics.EpicsReadable',
        epicstimeout = 3.0,
        description = 'Motion enabled for sample position 3',
        readpv = 'SQ:ICON:b2io1:MotionEnabledRBV',
    ),
    sp3_tx = device('nicos_sinq.icon.devices.enabledmotor.EnabledMotor',
        epicstimeout = 3.0,
        description = 'Sample Position 3, Translation X',
        motorpv = 'SQ:ICON:board4:SP3TX',
        errormsgpv = 'SQ:ICON:board4:SP3TX-MsgTxt',
        precision = 0.01,
        lock = 'sp3_allowed',
    ),
    sp3_ty_axis = device('nicos_sinq.icon.devices.enabledmotor.EnabledMotor',
        epicstimeout = 3.0,
        description = 'Sample Position 3, Translation Y axis',
        motorpv = 'SQ:ICON:board4:SP3TY',
        errormsgpv = 'SQ:ICON:board4:SP3TY-MsgTxt',
        precision = 0.01,
        lock = 'sp3_allowed',
        lowlevel = True,
    ),
    sp3_ty_brake = device('nicos.devices.epics.EpicsDigitalMoveable',
        epicstimeout = 3.0,
        description = 'Sample Position 3, Translation Y brake',
        readpv = 'SQ:ICON:b4io4:BrakeSP3TY',
        writepv = 'SQ:ICON:b4io4:BrakeSP3TY',
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
        epicstimeout = 3.0,
        description = 'Sample Position 3, Rotation Y',
        motorpv = 'SQ:ICON:board6:SP3RY',
        errormsgpv = 'SQ:ICON:board6:SP3RY-MsgTxt',
        precision = 0.01,
    ),
    sp3_rz = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'Sample Position 3, Rotation Z',
        motorpv = 'SQ:ICON:board6:SP3RZ',
        errormsgpv = 'SQ:ICON:board6:SP3RZ-MsgTxt',
        precision = 0.01,
    ),
)
