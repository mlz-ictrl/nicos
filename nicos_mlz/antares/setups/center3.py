description = 'Helium pressures'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    Ambient_pressure = device('nicos.devices.entangle.Sensor',
        description = 'Ambient pressure',
        tangodevice = tango_base + 'pressure/ambient',
    ),
    Flighttube_pressure = device('nicos.devices.entangle.Sensor',
        description = 'Pressure in flight tube',
        tangodevice = tango_base + 'pressure/flighttube',
    ),
    He_pressure = device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure of He bottle',
        tangodevice = tango_base + 'fzjdp_analog/Druckgeber',
        unit = 'bar',
    ),
)
