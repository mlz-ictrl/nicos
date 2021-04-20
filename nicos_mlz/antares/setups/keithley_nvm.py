description = 'Keithley Nanovoltmeter'
group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/keithley_nvm/'

devices = dict(
    nvm_volt = device('nicos.devices.entangle.Sensor',
        description = 'Nanovoltmeter voltage',
        tangodevice = tango_base + 'voltage',
        tangotimeout = 6.0,
        pollinterval = 8.0,
        maxage = 20.0,
        unit = 'V',
    ),
)
