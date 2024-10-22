description = 'Cryo-Con 24C cryo controller'
group = 'optional'

includes = ['alias_T']

tango_base = 'tango://localhost:10000/20t/'

devices = dict(
    T_dewar = device('nicos.devices.entangle.Sensor',
        description = 'Dewar bottle thermometer',
        tangodevice = tango_base + 'cryocon/t_dewar',
        pollinterval = 0.7,
        maxage = 2,
    ),
    T_shield = device('nicos.devices.entangle.Sensor',
        description = 'Shield thermometer',
        tangodevice = tango_base + 'cryocon/t_shield',
        pollinterval = 0.7,
        maxage = 2,
    ),
    T_ambient = device('nicos.devices.entangle.Sensor',
        description = 'Shield thermometer',
        tangodevice = tango_base + 'cryocon/t_ambient',
        pollinterval = 0.7,
        maxage = 2,
    ),
    T_coils = device('nicos.devices.entangle.Sensor',
        description = 'CX thermometer in VSM coils',
        tangodevice = tango_base + 'cryocon/t_coils',
        pollinterval = 0.7,
        maxage = 2,
    ),
)

