description = 'Neutron source'

group = 'lowlevel'

devices = dict(
    ReactorPower = device('nicos.devices.generic.VirtualCoder',
        description = 'FRM II reactor power',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (0, 20),
            warnlimits = (19, 21),
            pollinterval = 60,
            unit = 'MW',
            jitter = 0.1,
            curvalue = 19.9,
            speed = 0.05,
            maxage = 3600,
        ),
        fmtstr = '%.1f',
    ),
)

startupcode = """
ReactorPower._attached_motor._base_loop_delay = 60
"""
