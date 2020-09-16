description = 'Devices for the velocity selector'

selprefix = 'SQ:SANS:velsel:'

forbidden = [(3600, 4600), (7600, 9600)]

devices = dict(
    vs_speed = device('nicos_sinq.devices.velocity_selector.VSForbiddenMoveable',
        description = 'Velocity Selector Speed',
        writepv = selprefix + 'Speed',
        readpv = selprefix + 'I_DREH_RBV',
        epicstimeout = 3.0,
        abslimits = (3000, 28800),
        window = 20,
        forbidden_regions = forbidden,
    ),
    vs_tilt = device('nicos_sinq.devices.velocity_selector.VSTiltMotor',
        description = 'Velocity Selector Tilt',
        motorpv = 'SQ:SANS:mcu1:tilt',
        errormsgpv = 'SQ:SANS:mcu1:tilt-MsgTxt',
        precision = .01,
        epicstimeout = 3.0,
        limit = 50,
        vs_rotation = 'vs_speed'
    ),
    vs_lambda = device('nicos_sinq.devices.velocity_selector.VSLambda',
        description = 'Velocity Selector Wavelength Control',
        seldev = 'vs_speed',
        tiltdev = 'vs_tilt',
        unit = 'A',
        fmtstr = '%.2f',
    ),
    vs_vacuum = device('nicos.devices.epics.EpicsReadable',
        description = 'Velocity Selector Vaccum',
        readpv = selprefix + 'VAKUUM_RBV'
    ),
    vs_vibration = device('nicos.devices.epics.EpicsReadable',
        description = 'Velocity Selector Vibration',
        readpv = selprefix + 'Hz_RBV'
    ),
    vs_rot_t = device('nicos.devices.epics.EpicsReadable',
        description = 'Velocity Rotor Temperature',
        readpv = selprefix + 'T_ROT_RBV'
    ),
    vs_flow = device('nicos.devices.epics.EpicsReadable',
        description = 'Velocity Water Flow',
        readpv = selprefix + 'DURCHFL_RBV'
    ),
    vs_water_t = device('nicos.devices.epics.EpicsReadable',
        description = 'Velocity Water Temperature',
        readpv = selprefix + 'T_RUECK_RBV'
    ),
)
