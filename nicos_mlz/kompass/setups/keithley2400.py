description = 'Keithley 2400 SourceMeter'

group = 'optional'

tango_base = 'tango://kompasshw.kompass.frm2:10000/kompass/'

devices = dict(
    keithley_current = device('nicos.devices.entangle.PowerSupply',
        description = "Keithley current",
        tangodevice = tango_base + 'keithley2400/currentsource',
        fmtstr = '%.3f',
    ),
    keithley_resistance = device('nicos.devices.entangle.Sensor',
        description = "Keithley measured resistance",
        tangodevice = tango_base + 'keithley2400/resistance',
        fmtstr = '%.3f',
    ),
)
