description = 'LakeShore 340 cryo controller'

includes = ['alias_T']

devices = dict(
    T_ls340   = device('devices.taco.TemperatureController',
                      tacodevice = 'puma/ls340/control',
                      maxage = 2,
                      abslimits = (0, 300)),
    T_ls340_A = device('devices.taco.TemperatureSensor',
                      tacodevice = 'puma/ls340/sensora',
                      maxage = 2),
    T_ls340_B = device('devices.taco.TemperatureSensor',
                      tacodevice = 'puma/ls340/sensorb',
                      maxage = 2),
)

startupcode = '''
T.alias='T_ls340'
Ts.alias='T_ls340_B'
'''
