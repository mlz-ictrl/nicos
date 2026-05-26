
devices = dict(
    rc = device('nicos_mlz.erwin.devices.rc.RadialCollimator',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-float('inf'), float('inf')),
            unit = 'deg',
            speed = 10,
        ),
        frequency = 0.05,
    ),
)
