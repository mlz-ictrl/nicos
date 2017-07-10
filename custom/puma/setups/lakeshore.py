description = 'LakeShore 340 cryo controller'

group = 'optional'

includes = ['alias_T']

devices = dict(
    T_ls340   = device('nicos.devices.taco.TemperatureController',
                       description = 'Temperature Control with a LS340',
                       tacodevice = 'puma/ls340/control',
                       maxage = 11,
                       pollinterval = 5,
                       abslimits = (0, 550),
                      ),
    T_ls340_A = device('nicos.devices.taco.TemperatureSensor',
                       description = 'LS340 Sensor A (Cold head)',
                       tacodevice = 'puma/ls340/sensora',
                       maxage = 11,
                       pollinterval = 5,
                      ),
    T_ls340_B = device('nicos.devices.taco.TemperatureSensor',
                       description = 'LS340 Sensor B (sample)',
                       tacodevice = 'puma/ls340/sensorB',
                       maxage = 11,
                       pollinterval = 5,
                      ),
)

alias_config = {
    'T': {'T_ls340': 200},
    'Ts': {'T_ls340_B': 100, 'T_ls340_A': 90},
}
