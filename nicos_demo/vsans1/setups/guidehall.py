description = 'FRM II Neutron guide hall west infrastructure devices'

group = 'lowlevel'

devices = dict(
    Sixfold = device('nicos.devices.generic.ManualSwitch',
        description = 'Sixfold shutter status',
        states = ('open', 'closed'),
        pollinterval = 60,
        maxage = 120,
    ),
    Crane = device('nicos.devices.generic.ManualMove',
        description = 'The position of the crane in the guide '
        'hall West measured from the east end',
        abslimits = (0, 60),
        pollinterval = 5,
        maxage = 30,
        unit = 'm',
        fmtstr = '%.1f',
    ),
)
