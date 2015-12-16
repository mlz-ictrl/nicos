description = 'sample table devices'

group = 'optional'

includes = []

excludes = ['sc1', ]

devices = dict(
    SampleChanger = device('devices.generic.ManualSwitch',
                           description = 'Virtual Samplechanger with 22 '
                                         'positions',
                           states = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                                     11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                                     21, 22, ],
                           fmtstr = '%d',
                           ),
)
