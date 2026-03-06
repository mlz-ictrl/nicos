description = 'Setup for the ma11 dom motor'

devices = dict(
    dom = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample stick rotation',
        precision = 0.1,
        unit = 'deg',
        abslimits = (-360, 360),
    ),
)
