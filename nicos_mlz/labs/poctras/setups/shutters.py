description = 'Shutter devices'
group = 'lowlevel'

tango_base = 'tango://motorpi:10000/tomo/digital/'

devices = dict(
    shutter = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Instrument shutter',
        tangodevice = tango_base + 'shutter',
    ),
)
