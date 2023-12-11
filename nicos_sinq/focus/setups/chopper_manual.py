description = 'Setup for the FOCUS chopper'

excludes = ['chopper',]

devices = dict(
    ch1_speed = device('nicos.devices.generic.manual.ManualMove',
        description = 'Chopper 1 speed',
        unit = 'rpm',
        abslimits = (0, 20000),
        default = 1000
    ),
    ch2_speed = device('nicos.devices.generic.manual.ManualMove',
        description = 'Chopper 1 speed',
        unit = 'rpm',
        abslimits = (0, 20000),
        default = 500
    ),
    ch_phase = device('nicos.devices.generic.manual.ManualMove',
        description = 'Slave chopper phase offset',
        unit = 'degree',
        abslimits = (0, 360),
        default = 1000
    ),
    ch_ratio = device('nicos.devices.generic.manual.ManualMove',
        description = 'Ratio master/slave chopper',
        unit = '',
        abslimits = (1, 4),
        default = 2
    ),
)
