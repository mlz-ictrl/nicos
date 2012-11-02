description = 'FRM-II cryo box with two LakeShore controllers'
includes = ['system']

devices = dict(
    cryo   = device('devices.taco.temperature.TemperatureController',
                    tacodevice = '//toftofsrv/toftof/ls2/control',
                    userlimits = (0, 600),
                    abslimits = (0, 600),
                    p = 50,
                    i = 10,
                    d = 0,
                    ramp = 6.0,
                    unit = 'K',
                    fmtstr = '%g',
		    samplechannel = 'B',
                    sensor_a = 'cryo_a',
                    sensor_b = 'cryo_b',
                    sensor_c = None,
                    sensor_d = None),

    cryo_tube = device('devices.taco.temperature.TemperatureController',
                    tacodevice = '//toftofsrv/toftof/ls1/control',
                    userlimits = (0, 600),
                    abslimits = (0, 600),
                    p = 50,
                    i = 10,
                    d = 0,
                    ramp = 6.0,
                    unit = 'K',
                    fmtstr = '%g',
		    samplechannel = 'B',
                    sensor_a = 'cryo_c',
                    sensor_b = 'cryo_d',
                    sensor_c = None,
                    sensor_d = None),

    cryo_a = device('devices.taco.TemperatureSensor',
                    tacodevice = '//toftofsrv/toftof/ls2/sensora',
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_b = device('devices.taco.TemperatureSensor',
                    tacodevice = '//toftofsrv/toftof/ls2/sensorb',
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_c = device('devices.taco.TemperatureSensor',
                    tacodevice = '//toftofsrv/toftof/ls1/sensora',
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_d = device('devices.taco.TemperatureSensor',
                    tacodevice = '//toftofsrv/toftof/ls1/sensorb',
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_machine = device('devices.taco.DigitalOutput',
                    tacodevice = '//toftofsrv/toftof/ccr/compressor'),

    cryo_g = device('devices.taco.DigitalOutput',
                    tacodevice = '//toftofsrv/toftof/ccr/gas'),

    cryo_v = device('devices.taco.DigitalOutput',
                    tacodevice = '//toftofsrv/toftof/ccr/vacuum'),

    cryo_p = device('devices.taco.AnalogInput',
                    tacodevice = '//toftofsrv/toftof/ccr/p2'),
)

startupcode = """
T = cryo
Ts = cryo_b
SetEnvironment(Ts, T)
"""
