description = 'Keysight 33510A Function Generator'
group = 'optional'

includes = []

tango_base = 'tango://localhost:10000/antares/funcgen/'

devices = dict(
    ch2_amplitude = device('nicos.devices.entangle.AnalogOutput',
        description = 'Keysight Function Generator Channel 2 Amplitude',
        tangodevice = tango_base + 'ch2_amplitude',
        abslimits = (0, 5),
        unit = 'V',
    ),
    ch2_frequency = device('nicos.devices.entangle.AnalogOutput',
        description = 'Keysight Function Generator Channel 2 Frequency',
        tangodevice = tango_base + 'ch2_frequency',
        abslimits = (0, 10000000),
        unit = 'Hz',
    ),
)
