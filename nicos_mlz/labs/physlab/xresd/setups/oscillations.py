description = 'Sample oscillations'

group = 'optional'

devices = dict(
    x_osc = device('nicos.devices.generic.oscillator.Oscillator',
        description = 'X oscillation device',
        moveable = 'stx',
    ),
    y_osc = device('nicos.devices.generic.oscillator.Oscillator',
        description = 'Y oscillation device',
        moveable = 'sty',
    ),
    phis_osc = device('nicos.devices.generic.oscillator.Oscillator',
        description = 'Y oscillation device',
        moveable = 'phis',
    ),
)
