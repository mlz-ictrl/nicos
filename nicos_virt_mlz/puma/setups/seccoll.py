description = 'PUMA secondary collimator unit'

group = 'optional'

devices = dict(
    alpha2 = device('nicos.devices.generic.ManualSwitch',
        description = 'alpha2 - secondary collimator',
        states = [120, 60, 45, 30, 24, 20, 14],
        unit = 'min',
    ),
)
