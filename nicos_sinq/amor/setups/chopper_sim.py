description = 'Airbus chopper device in SINQ AMOR, Simulation'

display_order = 33

excludes = ['chopper']

devices = dict(
    ch1_speed = device('nicos.devices.generic.manual.ManualMove',
        description = 'Speed of the master chopper',
        unit = 'rpm',
        abslimits = (0, 2000),
        default = 500,
    ),
    ch1_position = device('nicos.devices.generic.manual.ManualMove',
        description = 'Phase of the master chopper',
        unit = 'degree',
        abslimits = (0, 360),
        default = 0,
        visibility = (),
    ),
    ch2_speed = device('nicos.devices.generic.manual.ManualMove',
        description = 'Speed of the slave chopper',
        unit = 'rpm',
        abslimits = (0, 2000),
        default = 500,
    ),
    ch2_position = device('nicos.devices.generic.manual.ManualMove',
        description = 'Phase of the slave chopper',
        unit = 'degree',
        abslimits = (0, 360),
        default = 13.5,
        visibility = (),
    ),
    ch2_gear_ratio = device('nicos.devices.generic.manual.ManualMove',
        description = 'Chopper gearing ratio',
        unit = '',
        abslimits = (0, 4),
        default = 1,
        visibility = (),
    ),
)
