description = 'Keithley 6221 current source, for susceptometer measurements'
group = 'optional'

tango_base = 'tango://mira1.mira.frm2:10000/mira/'

devices = dict(
    keithley_ampl = device('devices.tango.AnalogOutput',
                           description = 'Keithley amplitude',
                           tangodevice = tango_base + 'keithley/ampl',
                           abslimits = (0, 0.01),
                           unit = 'A',
                          ),
    keithley_freq = device('devices.tango.AnalogOutput',
                           description = 'Keithley frequency',
                           tangodevice = tango_base + 'keithley/freq',
                           abslimits = (1e-3, 1e5),
                           unit = 'Hz',
                          ),
)
