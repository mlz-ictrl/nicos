description = 'instrument shutter control'

devices = dict(
    instrument_shutter = device('nicos.devices.generic.ManualSwitch',
        description = 'Instrument Shutter Switcher with readback',
        states = ['open', 'close'],
    ),
)
