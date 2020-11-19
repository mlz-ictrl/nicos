description = 'Beam limiter at position 2'

group = 'lowlevel'

display_order = 30

pvprefix = 'SQ:ICON:board2:'

devices = dict(
    bl2left = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'Beam limiter 2 -X',
        motorpv = pvprefix + 'B2nX',
        errormsgpv = pvprefix + 'B2nX-MsgTxt',
        precision = 0.01,
        lowlevel = True,
    ),
    bl2right = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'Beam limiter 2 +X',
        motorpv = pvprefix + 'B2pX',
        errormsgpv = pvprefix + 'B2pX-MsgTxt',
        precision = 0.01,
        lowlevel = True,
    ),
    bl2bottom = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'Beam limiter 2 -Y',
        motorpv = pvprefix + 'B2nY',
        errormsgpv = pvprefix + 'B2nY-MsgTxt',
        precision = 0.01,
        lowlevel = True,
    ),
    bl2top = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'Beam limiter 2 +Y',
        motorpv = pvprefix + 'B2pY',
        errormsgpv = pvprefix + 'B2pY-MsgTxt',
        precision = 0.01,
        lowlevel = True,
    ),
    bl2 = device('nicos.devices.generic.slit.Slit',
        description = 'Beam limiter 2',
        opmode = 'offcentered',
        left = 'bl2left',
        right = 'bl2right',
        top = 'bl2top',
        bottom = 'bl2bottom',
    ),
    bl2_width = device('nicos.devices.generic.slit.WidthSlitAxis',
        description = 'Beam limiter 2 opening width',
        slit = 'bl2',
        unit = 'mm'
    ),
    bl2_height = device('nicos.devices.generic.slit.HeightSlitAxis',
        description = 'Beam limiter 2 opening width',
        slit = 'bl2',
        unit = 'mm'
    ),
    bl2_center_h = device('nicos.devices.generic.slit.CenterXSlitAxis',
        description = 'Beam limiter 2 horizontal center',
        slit = 'bl2',
        unit = 'mm'
    ),
    bl2_center_v = device('nicos.devices.generic.slit.CenterYSlitAxis',
        description = 'Beam limiter 2 vertical center',
        slit = 'bl2',
        unit = 'mm'
    ),
)
