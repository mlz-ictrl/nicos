description = "Pivot point at floor of samplechamber"

group = 'lowlevel'

devices = dict(
    pivot = device('devices.generic.ManualSwitch',
                   description = 'Pivot point at floor of samplechamber',
                   # description = 'Distance between sample position and pivot '
                   #               'point of the detector tube',
                   states = range(1, 14),
                   fmtstr = 'Point %d',
                   unit = '',
                  ),
)
