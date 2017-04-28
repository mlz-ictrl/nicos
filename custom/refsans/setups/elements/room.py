description = "manual numbers of sample pos"

group = 'lowlevel'

devices = dict(
    b2_sample = device('devices.generic.ManualMove',
                   description = 'Distanz b2 to sample',
                   abslimits = (100, 1000),
                   fmtstr = '%.2f',
                   unit = 'mm',
                  ),
    pivot = device('devices.generic.ManualSwitch',
                   description = 'Pivot point at floor of samplechamber',
                   # description = 'Distance between sample position and pivot '
                   #               'point of the detector tube',
                   states = list(range(1, 14)),
                   fmtstr = 'Point %d',
                   unit = '',
                  ),
)
