description = 'Beam limiter at position 1'

group = 'lowlevel'

display_order = 25

pvprefix = 'SQ:ICON:board1:'

devices = dict(
    bl1left = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'Beam limiter 1 -X',
        motorpv = pvprefix + 'B1nX',
        errormsgpv = pvprefix + 'B1nX-MsgTxt',
        precision = 0.01,
        lowlevel = True,
    ),
    bl1right = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'Beam limiter 1 +X',
        motorpv = pvprefix + 'B1pX',
        errormsgpv = pvprefix + 'B1pX-MsgTxt',
        precision = 0.01,
        lowlevel = True,
    ),
    bl1bottom = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'Beam limiter 1 -Y',
        motorpv = pvprefix + 'B1nY',
        errormsgpv = pvprefix + 'B1nY-MsgTxt',
        precision = 0.01,
        lowlevel = True,
    ),
    bl1top = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'Beam limiter 1 +Y',
        motorpv = pvprefix + 'B1pY',
        errormsgpv = pvprefix + 'B1pY-MsgTxt',
        precision = 0.01,
        lowlevel = True,
    ),
    bl1 = device('nicos.devices.generic.slit.Slit',
        description = 'Beam limiter 1',
        opmode = 'offcentered',
        left = 'bl1left',
        right = 'bl1right',
        top = 'bl1top',
        bottom = 'bl1bottom',
    ),
    bl1_width = device('nicos.devices.generic.slit.WidthSlitAxis',
        description = 'Beam limiter 1 opening width',
        slit = 'bl1',
        unit = 'mm'
    ),
    bl1_height = device('nicos.devices.generic.slit.HeightSlitAxis',
        description = 'Beam limiter 1 opening width',
        slit = 'bl1',
        unit = 'mm'
    ),
    bl1_center_h = device('nicos.devices.generic.slit.CenterXSlitAxis',
        description = 'Beam limiter 1 horizontal center',
        slit = 'bl1',
        unit = 'mm'
    ),
    bl1_center_v = device('nicos.devices.generic.slit.CenterYSlitAxis',
        description = 'Beam limiter 1 vertical center',
        slit = 'bl1',
        unit = 'mm'
    ),
)
