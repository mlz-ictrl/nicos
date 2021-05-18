description = 'Sample oscillation'

group = 'optional'

devices = dict(
    sample_osc = device('nicos.devices.generic.Oscillator',
        description = 'Oscillation of OMGS',
        moveable = 'omgs',
        unit = '',
        range = (-90, 90),
    ),
)
