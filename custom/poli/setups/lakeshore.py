description = 'LakeShore 340 cryo controller'
group = 'optional'

includes = ['alias_T']

devices = dict(
    T_ls340   = device('nicos.devices.taco.TemperatureController',
                       description = 'Lakeshore temperature regulation',
                       tacodevice = '//heidi22/heidi2/ls340/control',
                       pollinterval = 0.7,
                       maxage = 2,
                       abslimits = (0, 300),
                      ),
    T_ls340_A = device('nicos.devices.taco.TemperatureSensor',
                       description = 'Lakeshore sensor A',
                       tacodevice = '//heidi22/heidi2/ls340/sensa',
                       pollinterval = 0.7,
                       maxage = 2,
                      ),
    T_ls340_B = device('nicos.devices.taco.TemperatureSensor',
                       description = 'Lakeshore sensor B',
                       tacodevice = '//heidi22/heidi2/ls340/sensb',
                       pollinterval = 0.7,
                       maxage = 2,
                      ),
)

alias_config = {
    'T': {'T_ls340': 200},
    'Ts': {'T_ls340_A': 100, 'T_ls340_B': 90},
}
