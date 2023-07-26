description = 'Keysight 33510A Function Generator'
group = 'optional'

includes = []

tango_base = 'tango://172.28.77.82:10000/antares/funcgen/'

devices = dict(
    ch1_amplitude = device('nicos.devices.entangle.AnalogOutput',
        description = 'Keysight Function Generator Channel 1 Amplitude',
        tangodevice = tango_base + 'ch1_amplitude',
        abslimits = (-10, 10),
        unit = 'V',
    ),
    ch1_frequency = device('nicos.devices.entangle.AnalogOutput',
        description = 'Keysight Function Generator Channel 1 Frequency',
        tangodevice = tango_base + 'ch1_frequency',
        abslimits = (0, 0),
        unit = 'Hz',
    ),
)
