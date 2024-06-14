description = 'Justage laser devices'

group = 'lowlevel'

devices = dict(
    laser = device('nicos.devices.generic.ManualSwitch',
        description = 'Justage laser device',
        states = ['out', 'in'],
    ),
)
