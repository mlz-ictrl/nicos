description = 'sample table devices'

group = 'optional'

includes = []

excludes = ['sc2']

devices = dict(
    SampleChanger = device('devices.generic.ManualSwitch',
                           description = 'Virtual Samplechanger with 11 '
                                         'positions',
                           states = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                           fmtstr = '%d',
                           ),
)
