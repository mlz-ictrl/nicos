description = 'Devices for the attenuator'

devices = dict(
    att = device('nicos.devices.generic.manual.ManualSwitch',
        description = 'Attenuator choice',
        states = [0, 1, 2, 3, 4, 5],
    ),
)
