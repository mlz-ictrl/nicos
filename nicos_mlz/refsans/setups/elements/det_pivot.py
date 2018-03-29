description = 'Pivot point at floor of samplechamber'

group = 'lowlevel'

devices = dict(
    det_pivot = device('nicos.devices.generic.ManualSwitch',
        description = 'Pivot point at floor of samplechamber',
        states = range(1, 14 + 1),
        fmtstr = 'Point %d',
        unit = '',
    ),
)
