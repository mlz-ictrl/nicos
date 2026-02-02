description = 'Neutron source'

group = 'lowlevel'

devices = dict(
    ReactorPower = device('nicos.devices.generic.VirtualMotor',
        description = 'Reactor power',
        abslimits = (0, 20),
        pollinterval = 10,
        curvalue = 19.9,
        maxage = 61,
        unit = 'MW',
    ),
)
