description = 'FRM-II cryo box with two LakeShore controllers'
includes = ['system']

includes = ['alias_T']

nethost = 'toftofsrv'

devices = dict(
    cryo   = device('devices.taco.TemperatureController',
                    tacodevice = '//%s/toftof/ls2/control' % (nethost,),
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

    cryo_tube = device('devices.taco.TemperatureController',
                    tacodevice = '//%s/toftof/ls1/control' % (nethost,),
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
                    tacodevice = '//%s/toftof/ls2/sensora' % (nethost,),
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_b = device('devices.taco.TemperatureSensor',
                    tacodevice = '//%s/toftof/ls2/sensorb' % (nethost,),
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_c = device('devices.taco.TemperatureSensor',
                    tacodevice = '//%s/toftof/ls1/sensora' % (nethost,),
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_d = device('devices.taco.TemperatureSensor',
                    tacodevice = '//%s/toftof/ls1/sensorb' % (nethost,),
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_machine = device('devices.taco.DigitalOutput',
                    tacodevice = '//%s/toftof/ccr/compressor' % (nethost,)),

    cryo_g = device('devices.taco.DigitalOutput',
                    tacodevice = '//%s/toftof/ccr/gas' % (nethost,)),

    cryo_v = device('devices.taco.DigitalOutput',
                    tacodevice = '//%s/toftof/ccr/vacuum' % (nethost,)),

    cryo_p = device('devices.taco.AnalogInput',
                    tacodevice = '//%s/toftof/ccr/p2' % (nethost,)),
)

startupcode = """
T.alias = cryo
Ts.alias = cryo_b
AddEnvironment(T, Ts)
"""
