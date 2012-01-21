description = 'FRM-II cryo box with two LakeShore controllers'
includes = ['system']

devices = dict(
    cryo   = device('nicos.taco.temperature.TemperatureController',
                    tacodevice = '//toftofsrv/toftof/ls2/control',
                    userlimits = (0, 600),
                    abslimits = (0, 600),
                    p = 50,
                    i = 10,
                    d = 0,
                    rampRate = 0.1,
                    unit = 'K',
                    fmtstr = '%g',
                    sensor_a = 'cryo_a',
                    sensor_b = 'cryo_b',
                    sensor_c = None,
                    sensor_d = None),

    cryo_tube = device('nicos.taco.temperature.TemperatureController',
                    tacodevice = '//toftofsrv/toftof/ls1/control',
                    userlimits = (0, 400),
                    abslimits = (0, 400),
                    p = 50,
                    i = 10,
                    d = 0,
                    rampRate = 0.1,
                    unit = 'K',
                    fmtstr = '%g',
                    sensor_a = 'cryo_c',
                    sensor_b = 'cryo_d',
                    sensor_c = None,
                    sensor_d = None),

    cryo_a = device('nicos.taco.TemperatureSensor',
                    tacodevice = '//toftofsrv/toftof/ls2/sensora',
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_b = device('nicos.taco.TemperatureSensor',
                    tacodevice = '//toftofsrv/toftof/ls2/sensorb',
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_c = device('nicos.taco.TemperatureSensor',
                    tacodevice = '//toftofsrv/toftof/ls1/sensora',
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_d = device('nicos.taco.TemperatureSensor',
                    tacodevice = '//toftofsrv/toftof/ls1/sensorb',
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_machine = device('nicos.taco.DigitalOutput',
                    tacodevice = '//toftofsrv/toftof/ccr/compressor'),

    cryo_g = device('nicos.taco.DigitalOutput',
                    tacodevice = '//toftofsrv/toftof/ccr/gas'),

    cryo_v = device('nicos.taco.DigitalOutput',
                    tacodevice = '//toftofsrv/toftof/ccr/vacuum'),

    cryo_p = device('nicos.taco.AnalogInput',
                    tacodevice = '//toftofsrv/toftof/ccr/p1'),
)

startupcode = """
Ts = cryo
T = cryo_a
"""
