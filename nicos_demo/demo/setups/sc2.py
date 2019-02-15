description = 'sample table devices'

group = 'optional'

excludes = ['sc1']

devices = dict(
    SampleChanger = device('nicos.devices.generic.ManualSwitch',
        description = 'Virtual Samplechanger with 22 positions',
        states = [i for i in range(1, 23)],
        fmtstr = '%d',
    ),
)
