description = 'Toellner TOE7621 in constant voltage mode connected to Keysight 33510B function generator'
group = 'optional'

includes = []

excludes = ['keysight_funcgen_ch1']

tango_base = 'tango://localhost:10000/antares/funcgen/'

devices = dict(
        toellner_dc = device('nicos_mlz.antares.devices.ToellnerDc',
            description = 'test',
            max_voltage = 20,
            max_current = 16,
            mode = 'voltage',
            input_range = '10V',
            amplitude = 'ch1_amplitude',
            # frequency = 'ch1_frequency',
            pollinterval = 0.5,
            maxage = 5,
            abslimits = (-20,20),
            userlimits = (-20,20),
            unit = 'V'
        ),
        ch1_amplitude = device('nicos.devices.entangle.AnalogOutput',
            tangodevice = tango_base + 'ch1_amplitude',
            abslimits = (-10, 10),
            unit = 'V',
            visibility = (),
            # dcmode = True,
        ),
        ch1_frequency = device('nicos.devices.entangle.AnalogOutput',
            tangodevice = tango_base + 'ch1_frequency',
            abslimits = (0, 0),
            unit = 'Hz',
            visibility = (),
            # dcmode = True,
        ),
)
