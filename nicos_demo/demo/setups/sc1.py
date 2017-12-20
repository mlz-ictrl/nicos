description = 'sample table devices'

group = 'optional'

includes = []

excludes = ['sc2']

devices = dict(
    SampleChanger = device('nicos.devices.generic.ManualSwitch',
        description = 'Virtual Samplechanger with 11 positions',
        states = range(1, 12),
        fmtstr = '%d',
    ),
)
