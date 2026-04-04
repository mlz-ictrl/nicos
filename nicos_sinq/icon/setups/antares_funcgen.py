description = 'Keysight 33510A Function Generator'
group = 'optional'

includes = []

tango_base = 'tango://antareslab01.psi.ch:10000/antares/funcgen/'

devices = dict(
        ch1_amplitude = device('nicos.devices.entangle.AnalogOutput',
            description = 'Keysight Function Generator Channel 1 Amplitude',
            tangodevice = tango_base + 'ch1_amplitude',
            unit = 'V',
        ),
        ch1_frequency = device('nicos.devices.entangle.AnalogOutput',
            description = 'Keysight Function Generator Channel 1 Frequency',
            tangodevice = tango_base + 'ch1_frequency',
            unit = 'Hz',
        ),
)
