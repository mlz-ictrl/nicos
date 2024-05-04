description = 'Neutron source'

group = 'lowlevel'

devices = dict(
    ReactorPower = device('nicos.devices.generic.VirtualMotor',
        description = 'Reactor power',
        abslimits = (0, 20),
        pollinterval = 10,
        maxage = 75,
        unit = 'MW',
        jitter = 0.1,
        curvalue = 19.9,
        fmtstr = '%.1f',
    ),
)
