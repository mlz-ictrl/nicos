description = 'LakeShore 340 cryo controller'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://puma5.puma.frm2.tum.de:10000/puma/ls340/'

devices = dict(
    T_ls340 = device('nicos.devices.tango.TemperatureController',
        description = 'Temperature Control with a LS340',
        tangodevice = tango_base + 'control',
        maxage = 11,
        pollinterval = 5,
        abslimits = (0, 550),
        p = 20,
        i = 10,
        d = 0,
        # maxpower = 50
        # resistance = 25
        timeout = 600,
        precision = 1.0,
        window = 60,
    ),
    T_ls340_A = device('nicos.devices.tango.Sensor',
        description = 'LS340 Sensor A (Cold head)',
        tangodevice = tango_base + 'sensora',
        maxage = 11,
        pollinterval = 5,
    ),
    T_ls340_B = device('nicos.devices.tango.Sensor',
        description = 'LS340 Sensor B (sample)',
        tangodevice = tango_base + 'sensorb',
        maxage = 11,
        pollinterval = 5,
    ),
)

alias_config = {
    'T': {'T_ls340': 200},
    'Ts': {'T_ls340_B': 100, 'T_ls340_A': 90},
}
