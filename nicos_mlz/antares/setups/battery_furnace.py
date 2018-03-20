description = 'battery furnace'
group = 'optional'

includes = ['alias_T']

devices = dict(
    T_bat_A = device('nicos.devices.taco.TemperatureController',
        description = 'CCR0 temperature regulation',
        tacodevice = '//172.25.20.210/mpfc/ls340/control1',
        pollinterval = 1,
        maxage = 6,
        abslimits = (0, 500),
    ),
    T_bat_B = device('nicos.devices.taco.TemperatureController',
        description = 'CCR0 temperature regulation',
        tacodevice = '//172.25.20.210/mpfc/ls340/control2',
        pollinterval = 1,
        maxage = 6,
        abslimits = (0, 500),
    ),
)

alias_config = {
    'T': {
        'T_bat_B': 100
    },
}
