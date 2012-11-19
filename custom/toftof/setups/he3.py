description = 'He 3 insert and gas handling'
includes = ['system']

includes = ['alias_T']

nethost="cryo1.toftof.frm2"

devices = dict(
    he3 = device('devices.taco.TemperatureController',
                 tacodevice = '//%s/cryo/ls370/control' % (nethost, ),
                 userlimits = (0, 300),
                 abslimits = (0, 300),
                 p = 50,
                 i = 10,
                 d = 0,
                 ramprate = 0.1,
                 unit = 'K',
                 fmtstr = '%g',
                 sensor_a = 'sensor_a',
                 sensor_b = 'sensor_b',
                 sensor_c = None,
                 sensor_d = None),

    sensor_a = device('devices.taco.TemperatureSensor',
                 tacodevice = '//%s/cryo/ls370/sensora' % (nethost, ),
                 unit = 'K',
                 fmtstr = '%g'),

    sensor_b = device('devices.taco.TemperatureSensor',
                 tacodevice = '//%s/cryo/ls370/sensorb' % (nethost, ),
                 unit = 'K',
                 fmtstr = '%g'),
)

startupcode = """
T.alias = he3
Ts.alias = sensor_a
AddEnvironment(T, Ts)
"""
