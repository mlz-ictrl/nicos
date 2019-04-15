description = 'small goniometer to adjust sample on gonio'

group = 'optional'

devices = dict(
    gonio_top_theta = device('nicos.devices.generic.VirtualMotor',
        description = 'Top Theta axis motor',
        # abslimits = (-500, 500),
        abslimits = (-9.5, 10.5),
        speed = 5.,
        unit = 'deg',
    ),
    gonio_top_z = device('nicos.devices.generic.Axis',
        description = 'Top Z axis with offset',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-0.05, 15),
            speed = 0.05,
            unit = 'mm',
        ),
        precision = 0.01,
        offset = 0.0,
    ),
    gonio_top_phi = device('nicos.devices.generic.VirtualMotor',
        description = 'Top Phi axis motor',
        abslimits = (-10.5, 10.5),
        speed = 5.,
        unit = 'deg',
    ),
)
