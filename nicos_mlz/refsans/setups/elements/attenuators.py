description = 'Attenuators in beam guide chamber'

group = 'lowlevel'

devices = dict(
    attenuator1 = device('nicos.devices.generic.ManualSwitch',
        description = 'attenuator at zb0',
        states = ['out', 'in'],
    ),
    attenuator2 = device('nicos.devices.generic.ManualSwitch',
        description = 'attenuator at zb1',
        states = ['out', 'in'],
    ),
)
