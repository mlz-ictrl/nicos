description = 'Collimator changer devices'

group = 'lowlevel'

devices = dict(
    collchanger = device('nicos.devices.generic.ManualSwitch',
        description = 'Collimator insert device',
        states = ['out', 'in'],
    ),
)
