description = 'Devices for the velocity selector'

selprefix = 'SQ:SANS:velsel:'

forbidden = [(1, 1600), (3300, 5200), (6600, 10000), (28300, 30000)]

devices = dict(
    vs_speed = device('nicos_sinq.devices.velocity_selector.VSForbiddenMoveable',
        description = 'Velocity Selector Speed',
        writepv = selprefix + 'req_speed',
        readpv = selprefix + 'speed_filtered_rbv',
        epicstimeout = 3.0,
        abslimits = (1600, 28300),
        precision = 20,
        forbidden_regions = forbidden,
        unit = 'rpm',
    ),
    vs_tilt = device('nicos_sinq.devices.velocity_selector.VSTiltMotor',
        description = 'Velocity Selector Tilt',
        motorpv = 'SQ:SANS:turboPmac1:tilt',
        errormsgpv = 'SQ:SANS:turboPmac1:tilt-MsgTxt',
        precision = .01,
        limit = 50,
        vs_rotation = 'vs_speed',
        can_disable = True,
    ),
    vs_lambda = device('nicos_sinq.devices.velocity_selector.VSLambda',
        description = 'Velocity Selector Wavelength Control',
        seldev = 'vs_speed',
        tiltdev = 'vs_tilt',
        unit = 'A',
        fmtstr = '%.2f',
    ),
    vs_vacuum = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Velocity Selector Vacuum',
        readpv = selprefix + 'vacuum_rbv'
    ),
    vs_vibration = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Velocity Selector Vibration',
        readpv = selprefix + 'vibration_rbv'
    ),
    vs_rot_t = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Velocity Rotor Temperature',
        readpv = selprefix + 'rotor_temp_rbv'
    ),
    vs_flow = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Velocity Water Flow',
        readpv = selprefix + 'cw_flow_rate_rbv'
    ),
    vs_water_tin = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Velocity Water Temperature inlet',
        readpv = selprefix + 'cw_temp_inlet_rbv'
    ),
    vs_water_tout = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Velocity Water Temperature outlet',
        readpv = selprefix + 'cw_temp_outlet_rbv'
    ),
    vs_cbv = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Characteristic Bearing Value, front bearing',
        readpv = selprefix + 'cbv_rbv'
    ),
)
