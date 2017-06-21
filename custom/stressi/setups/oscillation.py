description = 'Sample oscillation'

group = 'optional'

devices = dict(
    sample_osc = device('devices.generic.oscillator.Oscillator',
                        description = 'Sample oscillation device',
                        moveable = 'omgs',
                        range = (-90, 90)
                       ),
)
