description = 'battery furnace'
group = 'plugplay'

includes = ['alias_T']

nethost = 'mpfc01'

devices = dict(
    T_bat_A = device('nicos.devices.taco.TemperatureController',
        description = 'CCR0 temperature regulation',
        tacodevice = '//%s/mpfc/ls340/control1' % nethost,
        pollinterval = 1,
        maxage = 6,
        abslimits = (0, 500),
    ),
    T_bat_B = device('nicos.devices.taco.TemperatureController',
        description = 'CCR0 temperature regulation',
        tacodevice = '//%s/mpfc/ls340/control2' % nethost,
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
