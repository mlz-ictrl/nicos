description = 'Basic Setup for Experiments in Experimental Chamber 1'
group = 'basic'

includes = ['basic', 'sbl', 'detector_four']

devices = dict(
    sry_multi_1 = device('nicos.devices.generic.VirtualMotor',
        description = 'Multitomo sample 1 rotation',
        precision = 0.01,
        abslimits = (-400, 400),
        pollinterval = 5,
        maxage = 12,
        unit = 'deg',
    ),
    sry_multi_2 = device('nicos.devices.generic.VirtualMotor',
        description = 'Multitomo sample 2 rotation',
        precision = 0.01,
        abslimits = (-400, 400),
        pollinterval = 5,
        maxage = 12,
        unit = 'deg',
    ),
    sry_multi_3 = device('nicos.devices.generic.VirtualMotor',
        description = 'Multitomo sample 3 rotation',
        precision = 0.01,
        abslimits = (-400, 400),
        pollinterval = 5,
        maxage = 12,
        unit = 'deg',
    ),
    sry_multi_4 = device('nicos.devices.generic.VirtualMotor',
        description = 'Multitomo sample 4 rotation',
        precision = 0.01,
        abslimits = (-400, 400),
        pollinterval = 5,
        maxage = 12,
        unit = 'deg',
    ),
)
