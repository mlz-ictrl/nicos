description = 'Basic Setup for Experiments in Experimental Chamber 1'
group = 'basic'

includes = ['basic', 'sbl', 'detector_four']

devices = dict(
    sry1 = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample 1 rotation around Y',
        precision = 0.01,
        abslimits = (-999999, 999999),
        pollinterval = 5,
        maxage = 12,
        unit = 'deg',
    ),
    sry2 = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample 2 rotation around Y',
        precision = 0.01,
        abslimits = (-999999, 999999),
        pollinterval = 5,
        maxage = 12,
        unit = 'deg',
    ),
    sry3 = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample 3 rotation around Y',
        precision = 0.01,
        abslimits = (-999999, 999999),
        pollinterval = 5,
        maxage = 12,
        unit = 'deg',
    ),
    sry4 = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample 4 rotation around Y',
        precision = 0.01,
        abslimits = (-999999, 999999),
        pollinterval = 5,
        maxage = 12,
        unit = 'deg',
    ),
)
