description = 'Devices for the polariser'

excludes = ['collimator_s7']

devices = dict(
    pol = device('nicos.devices.generic.manual.ManualSwitch',
        description = 'Polariser choice',
        states = ['in', 'out'],
    ),
)
