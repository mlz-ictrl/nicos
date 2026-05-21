description = 'Neutron source'

group = 'lowlevel'

devices = dict(
    ReactorPower = device('nicos.devices.generic.VirtualMotor',
        description = 'FRM II reactor power',
        abslimits = (0, 20),
        warnlimits = (19, 21),
        fmtstr = '%.1f',
        jitter = 0.1,
        pollinterval = 60,
        maxage = 3600,
        unit = 'MW',
        curvalue = 19.9,
    ),
)
