description = 'Helium pressures'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    center3_sens1 = device('devices.taco.AnalogInput',
        description = 'Center 3 Sensor 1',
        tacodevice = 'antares/center3/sens1',
        unit = 'mbar',
    ),
    center3_sens2 = device('devices.taco.AnalogInput',
        description = 'Center 3 Sensor 2',
        tacodevice = 'antares/center3/sens2',
        unit = 'mbar',
    ),
    He_pressure = device('devices.tango.AnalogInput',
        description = 'Pressure of He bottle',
        tangodevice = tango_base + 'fzjdp_analog/Druckgeber',
        unit = 'bar',
    ),
)
