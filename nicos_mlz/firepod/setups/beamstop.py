description = 'Beamstop devices'

group = 'lowlevel'

devices = dict(
    bs = device('nicos.devices.generic.ManualSwitch',
        description = 'Beamstop selection device',
        states = ['dump', 'camera'],
    ),
)
