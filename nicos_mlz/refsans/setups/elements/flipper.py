description = 'Refsans_flipper special HW; but NOT yet!'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base'] + 'test/flipper/'

devices = dict(
    guide = device('nicos.devices.tango.AnalogInput',
        description = 'Temperature of Flipping Guide',
        tangodevice = tango_base + 'guide_temp',
    ),
    coil = device('nicos.devices.tango.AnalogInput',
        description = 'Temperature of Flipping Coil',
        tangodevice = tango_base + 'coil_temp',
    ),
    current = device('nicos.devices.tango.WindowTimeoutAO',
        description = 'Current of Flipping Coil',
        tangodevice = tango_base + 'current',
        precision = 0.1,
    ),
    frequency = device('nicos.devices.tango.AnalogInput',
        description = 'Frequency of Flipping Field',
        tangodevice = tango_base + 'frequency',
    ),
    flipper = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Flipper',
        tangodevice = tango_base + 'flipper',
        mapping = dict(ON = 1, OFF = 0),
    ),
)
