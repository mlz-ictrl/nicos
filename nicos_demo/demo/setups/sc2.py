description = 'sample table devices'

group = 'optional'

includes = []

excludes = ['sc1']

devices = dict(
    SampleChanger = device('nicos.devices.generic.ManualSwitch',
        description = 'Virtual Samplechanger with 22 positions',
        states = range(1, 23),
        fmtstr = '%d',
    ),
)
