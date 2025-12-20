devices = dict(
        det_rot = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-180, 180),
            unit = 'deg',
        ),
        sample_rot = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-180, 180),
            unit = 'deg',
        ),
)
