description = 'Agilent 33210A arbitrary waveform generator, for electrical steel sheet measurement'
group = 'optional'

includes = []

tango_base = 'tango://antareshw.antares.frm2:10000/antares/fg/'

devices = dict(
    funcgen_amp = device('nicos.devices.tango.AnalogOutput',
        description = 'Agilent function generator Amplitude',
        tangodevice = tango_base + 'ch1_amplitude',
        abslimits = (0, 5),
        unit = 'V',
    ),
    funcgen_freq = device('nicos.devices.tango.AnalogOutput',
        description = 'Agilent function generator Frequency',
        tangodevice = tango_base + 'ch1_frequency',
        abslimits = (0, 10000000),
        unit = 'Hz',
    ),
)