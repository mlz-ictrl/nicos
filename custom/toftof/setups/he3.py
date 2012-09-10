description = 'He 3 insert and gas handling'
includes = ['system']

nethost="cryo1.toftof.frm2"

devices = dict(
    he3 = device('nicos.taco.temperature.TemperatureController',
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

    sensor_a = device('nicos.taco.temperature.TemperatureSensor',
                 tacodevice = '//%s/cryo/ls370/sensora' % (nethost, ),
                 unit = 'K',
                 fmtstr = '%g'),

    sensor_b = device('nicos.taco.temperature.TemperatureSensor',
                 tacodevice = '//%s/cryo/ls370/sensorb' % (nethost, ),
                 unit = 'K',
                 fmtstr = '%g'),
)

startupcode = """
T = he3
Ts = sensor_a
SetEnvironment(Ts, T)
"""
