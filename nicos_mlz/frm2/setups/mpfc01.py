description = 'battery furnace'
group = 'plugplay'

includes = ['alias_T']

tango_base = 'tango://mpfc01:10000/mpfc/ls340/'

devices = dict(
    T_bat_A = device('nicos.devices.entangle.TemperatureController',
        description = 'CCR0 temperature regulation',
        tangodevice = tango_base + 'control1',
        pollinterval = 1,
        maxage = 6,
        abslimits = (0, 500),
    ),
    T_bat_B = device('nicos.devices.entangle.TemperatureController',
        description = 'CCR0 temperature regulation',
        tangodevice = tango_base + 'control2',
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
