description = 'Devices for the collimator'

excludes = ['collimator_s7']

devices = dict(
    coll = device('nicos.devices.generic.manual.ManualSwitch',
        description = 'Collimation length',
        states = [2, 3, 4.5, 6, 8, 11, 15, 18],
    ),
)
