description = 'frequency counter, fg1 and fg2'

includes = []

# group = 'lowlevel'

tango_base = 'tango://sans1hw.sans1.frm2:10000/sans1/tisane'

devices = dict(
    tisane_fc = device('devices.tango.Sensor',
                       description = "Frequency counter for chopper signal",
                       tangodevice = "%s/fc1_frequency" % tango_base,
                       unit = "Hz",
                      ),
    tisane_fg1 = device('sans1.tisane.Burst',
                        description = "Signal-generator for sample tisane signal",
                        tangodevice = "%s/fg1_burst" % tango_base,
                        frequency = 1000,
                        amplitude = 2.5,
                        offset = 1.3,
                        shape = 'square',
                        duty = 50,
                        mapping = dict(On=1, Off=0),
                       ),
    tisane_fg2 = device('sans1.tisane.Burst',
                        description = "Signal-generator for detector tisane signal",
                        tangodevice = "%s/fg2_burst" % tango_base,
                        frequency = 1000,
                        amplitude = 5.0,
                        offset = 1.3,
                        shape = 'square',
                        duty = 50,
                        mapping = dict(On=1, Off=0),
                       ),
)
