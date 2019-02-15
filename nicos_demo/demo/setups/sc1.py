description = 'sample table devices'

group = 'optional'

excludes = ['sc2']

devices = dict(
    SampleChanger = device('nicos.devices.generic.ManualSwitch',
        description = 'Virtual Samplechanger with 11 positions',
        states = [i for i in range(1, 12)],
        fmtstr = '%d',
    ),
)
