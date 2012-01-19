description = 'cryo'
includes = ['system']

devices = dict(
    cryo = device('nicos.taco.temperature.TemperatureController',
                 tacodevice = '',
                 userlimits = (0, 600),
                 abslimits = (0, 600),
                 p = 50,
                 i = 10,
                 d = 0,
                 rampRate = 0.1,
                 unit = 'K',
                 fmtstr = '%g'),

    cryo_tube = device('nicos.taco.temperature.TemperatureController',
                 tacodevice = '',
                 userlimits = (0, 400),
                 abslimits = (0, 400),
                 p = 50,
                 i = 10,
                 d = 0,
                 rampRate = 0.1,
                 unit = 'K',
                 fmtstr = '%g'),

    cryo_a = device('nicos.taco.temperature.TemperatureSensor',
                 tacodevice = '//toftofsrv/toftof/.../sensor_a',
                 unit = 'K',
                 fmtstr = '%g'),

    cryo_b = device('nicos.taco.temperature.TemperatureSensor',
                 tacodevice = '//toftofsrv/toftof/.../sensor_b',
                 unit = 'K',
                 fmtstr = '%g'),

    cryo_c = device('nicos.taco.temperature.TemperatureSensor',
                 tacodevice = '//toftofsrv/toftof/.../sensor_c',
                 unit = 'K',
                 fmtstr = '%g'),

    cryo_d = device('nicos.taco.temperature.TemperatureSensor',
                 tacodevice = '//toftofsrv/toftof/.../sensor_d',
                 unit = 'K',
                 fmtstr = '%g'),
)

startupcode = """
Ts = cryo
T = cryo_a
"""
