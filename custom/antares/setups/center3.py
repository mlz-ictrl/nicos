description = 'Center 3'

group = 'optional'

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
)
