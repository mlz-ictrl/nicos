description = 'Neutron source'

group = 'lowlevel'

devices = dict(
    ReactorPower = device('nicos.devices.generic.VirtualMotor',
        description = 'Reactor power',
        abslimits = (0, 20),
        pollinterval = 60,
        maxage = 61,
        unit = 'MW',
        jitter = 0.1,
    ),
)
