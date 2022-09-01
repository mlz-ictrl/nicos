description = 'Neutron source'

group = 'lowlevel'

devices = dict(
    ReactorPower = device('nicos.devices.generic.VirtualCoder',
        description = 'Reactor power',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (0, 20),
            warnlimits = (19, 21),
            pollinterval = 60,
            maxage = 61,
            unit = 'MW',
            jitter = 0.1,
            curvalue = 19.8,
            speed = 0.05,
        ),
    ),
)

startupcode = """
ReactorPower._attached_motor._base_loop_delay = 60
"""
