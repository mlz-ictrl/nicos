description = 'He 3 insert and gas handling'

group = 'optional'

includes = ['system', 'alias_T']

nethost="cryo1.toftof.frm2"

devices = dict(
    he3 = device('devices.taco.TemperatureController',
                 description = 'The control device to the sample',
                 tacodevice = '//%s/cryo/ls370/control' % (nethost, ),
                 abslimits = (0, 300),
                 unit = 'K',
                 fmtstr = '%.3f',
                 pollinterval = 5,
                 maxage = 6,
                ),

    sensor_a = device('devices.taco.TemperatureSensor',
                      description = 'Temperature at the sample',
                      tacodevice = '//%s/cryo/ls370/sensora' % (nethost, ),
                      unit = 'K',
                      fmtstr = '%.3f',
                      pollinterval = 5,
                      maxage = 6,
                     ),

    sensor_b = device('devices.taco.TemperatureSensor',
                      description = '',
                      tacodevice = '//%s/cryo/ls370/sensorb' % (nethost, ),
                      unit = 'K',
                      fmtstr = '%.3f',
                      pollinterval = 5,
                      maxage = 6,
                     ),
)

startupcode = """
T.alias = he3
Ts.alias = sensor_a
AddEnvironment(T, Ts)
"""
