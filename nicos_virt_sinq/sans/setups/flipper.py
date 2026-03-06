description = 'Devices for the spin flipper at SANS, implemented with a HAMEG 8131'

devices = dict(
    flip_freq = device('nicos.devices.generic.ManualMove',
        description = 'Set frequency',
        abslimits = (100E-6, 15E06),
        unit = 'Hz',
    ),
    flip_amp = device('nicos.devices.generic.ManualMove',
        description = 'Set amplitude',
        abslimits = (20E-3, 20.),
        unit = 'V',
    ),
    flip_off = device('nicos.devices.generic.ManualMove',
        description = 'Set offset',
        abslimits = (-5, 5),
        unit = 'V',
    ),
    flip_state = device('nicos.devices.generic.ManualSwitch',
        description = 'Set state, on/off',
        states = ['off', 'on'],
    ),
)
