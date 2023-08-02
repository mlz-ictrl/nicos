description = 'Devices for the velocity selector'

selprefix = 'SQ:SANS-LLB:VS:'

forbidden = [(3600, 4600), (7600, 9600)]

devices = dict(
    vs_speed = device('nicos_sinq.devices.velocity_selector.VSForbiddenMoveable',
        description = 'Velocity Selector Speed',
        writepv = selprefix + 'Speed',
        readpv = selprefix + 'ASPEED_RBV',
        epicstimeout = 3.0,
        abslimits = (3100, 28800),
        precision = 20,
        forbidden_regions = forbidden,
    ),
    vs_vacuum = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Velocity Selector Vaccum',
        readpv = selprefix + 'VACUUM_RBV'
    ),
    vs_vibration = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Velocity Selector Vibration',
        readpv = selprefix + 'VIBRT_RBV'
    ),
    vs_rot_t = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Velocity Rotor Temperature',
        readpv = selprefix + 'RTEMP_RBV'
    ),
    vs_flow = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Velocity Water Flow',
        readpv = selprefix + 'WFLOW_RBV'
    ),
    vs_water_t = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Velocity Water Temperature',
        readpv = selprefix + 'WOUTT_RBV'
    ),
    wavelength = device('nicos_sinq.sans-llb.devices.wavelength.SANSWL',
        description = 'Device which translates wavelength to'
        'VS speed',
        a = .2285,
        b = 7432.09,
        speed = 'vs_speed',
        unit = 'A'
    ),
)
