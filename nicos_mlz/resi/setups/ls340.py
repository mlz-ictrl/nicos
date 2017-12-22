description = 'LakeShore 340 cryo controller'

includes = ['alias_T']

group = 'optional'

devices = dict(
    T_ls340 = device('nicos.devices.taco.TemperatureController',
        description = 'RESI lakeshore controller',
        tacodevice = '//resictrl/resi/ls340/ncontrol',
        maxage = 10,
        pollinterval = 5,
        abslimits = (0, 300),
    ),
    T_ls340_A = device('nicos.devices.taco.TemperatureSensor',
        description = 'RESI lakeshore Sensor A',
        tacodevice = '//resictrl/resi/ls340/nsensa',
        maxage = 10,
        pollinterval = 5,
    ),
    T_ls340_B = device('nicos.devices.taco.TemperatureSensor',
        description = 'RESI lakeshore Sensor B',
        tacodevice = '//resictrl/resi/ls340/nsensb',
        maxage = 10,
        pollinterval = 5,
    ),
)

alias_config = {
    'T': {'T_ls340': 200},
    'Ts': {'T_ls340_B': 100, 'T_ls340_A': 90},
}
