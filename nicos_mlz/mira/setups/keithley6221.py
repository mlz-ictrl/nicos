description = 'Keithley 6221 current source, for susceptometer measurements'
group = 'optional'

tango_base = 'tango://mira1.mira.frm2:10000/mira/'

devices = dict(
    keithley_ampl = device('nicos.devices.tango.AnalogOutput',
                           description = 'Keithley amplitude',
                           tangodevice = tango_base + 'keithley/ampl',
                           unit = 'A',
                          ),
    keithley_freq = device('nicos.devices.tango.AnalogOutput',
                           description = 'Keithley frequency',
                           tangodevice = tango_base + 'keithley/freq',
                           unit = 'Hz',
                          ),
)
