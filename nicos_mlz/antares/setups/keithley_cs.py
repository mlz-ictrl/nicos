description = 'Keithley 6221 current source, for susceptometer measurements'
group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/keithley_currentsource/'

devices = dict(
    cs_curr = device('nicos.devices.entangle.AnalogOutput',
        description = 'Keithley currentsource dc current',
        tangodevice = tango_base + 'curr',
        abslimits = (0, 0.1),
        unit = 'A',
    ),
)
