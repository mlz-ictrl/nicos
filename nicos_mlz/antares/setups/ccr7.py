description = 'LakeShore 340 cryo controller for CCR7 cryostat'
group = 'optional'

includes = ['alias_T']

tango_base = 'tango://antareshw.antares.frm2.tum.de:10000/antares/ls340se/'

devices = dict(
    T_ccr7 = device('nicos.devices.tango.TemperatureController',
        description = 'CCR7 temperature regulation',
        tangodevice = tango_base + 'control',
        pollinterval = 1,
        maxage = 6,
        abslimits = (0, 300),
    ),
    T_ccr7_A = device('nicos.devices.tango.Sensor',
        description = 'CCR7 sensor A',
        tangodevice = tango_base + 'sensa',
        pollinterval = 1,
        maxage = 6,
    ),
    T_ccr7_B = device('nicos.devices.tango.Sensor',
        description = 'CCR7 sensor B',
        tangodevice = tango_base + 'sensb',
        pollinterval = 1,
        maxage = 6,
    ),
)

alias_config = {
    'T': {
        'T_ccr7': 100
    },
    'Ts': {
        'T_ccr7_A': 100,
        'T_ccr7_B': 90,
    },
}
