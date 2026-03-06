description = 'SANS shutter via SPS-5'

group = 'lowlevel'

devices = dict(
    shutter = device('nicos.devices.generic.ManualSwitch',
        description = 'Shutter SPS',
        states = ['open', 'closed'],
    ),
)
