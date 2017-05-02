description = 'LakeShore 340 cryo controller for CCR7 cryostat'
group = 'optional'

includes = ['alias_T']

devices = dict(
    T_ccr7 = device('nicos.devices.taco.TemperatureController',
        description = 'CCR7 temperature regulation',
        tacodevice = '//antaressrv/antares/ls340se/control',
        pollinterval = 1,
        maxage = 6,
        abslimits = (0, 300),
    ),
    T_ccr7_A = device('nicos.devices.taco.TemperatureSensor',
        description = 'CCR7 sensor A',
        tacodevice = '//antaressrv/antares/ls340se/sensa',
        pollinterval = 1,
        maxage = 6,
    ),
    T_ccr7_B = device('nicos.devices.taco.TemperatureSensor',
        description = 'CCR7 sensor B',
        tacodevice = '//antaressrv/antares/ls340se/sensb',
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
