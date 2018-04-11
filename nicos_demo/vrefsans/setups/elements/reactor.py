description = 'Neutron source'

group = 'lowlevel'

devices = dict(
    ReactorPower = device('nicos.devices.generic.VirtualMotor',
        description = 'Reactor power',
        abslimits = (0, 20),
        warnlimits = (19, 21),
        pollinterval = 10,
        maxage = 61,
        unit = 'MW',
        jitter = 0.1,
        curvalue = 19.8,
    ),
)
