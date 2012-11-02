description = 'FRM-II CCR box with LakeShore LS336 controller'
includes = ['system']

nethost = 'ccr17.toftof.frm2'

devices = dict(
    cryo   = device('devices.taco.temperature.TemperatureController',
                    tacodevice = '//%s/ccr/ls336/control2' % (nethost, ),
                    userlimits = (0, 600),
                    abslimits = (0, 600),
                    p = 50,
                    i = 10,
                    d = 0,
                    ramp = 6.0,
                    unit = 'K',
                    fmtstr = '%g',
		    samplechannel = 'D',
                    sensor_a = 'cryo_c',
                    sensor_b = 'cryo_d',
                    sensor_c = None,
                    sensor_d = None),

    cryo_tube = device('devices.taco.temperature.TemperatureController',
                    tacodevice = '//%s/ccr/ls336/control1' % (nethost, ),
                    userlimits = (0, 400),
                    abslimits = (0, 400),
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

    cryo_a = device('devices.taco.TemperatureSensor',
                    tacodevice = '//%s/ccr/ls336/sensora' % (nethost, ),
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_b = device('devices.taco.TemperatureSensor',
                    tacodevice = '//%s/ccr/ls336/sensorb' % (nethost, ),
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_c = device('devices.taco.TemperatureSensor',
                    tacodevice = '//%s/ccr/ls336/sensorc' % (nethost, ),
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_d = device('devices.taco.TemperatureSensor',
                    tacodevice = '//%s/ccr/ls336/sensord' % (nethost, ),
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_machine = device('devices.taco.DigitalOutput',
                    tacodevice = '//%s/ccr/plc/on' % (nethost, )),

    cryo_gs = device('devices.taco.DigitalOutput',
                    lowlevel = True,
                    tacodevice = '//%s/ccr/plc/gas' % (nethost, )),

    cryo_gr = device('devices.taco.DigitalInput',
                    lowlevel = True,
                    tacodevice = '//%s/ccr/plc/fbgas' % (nethost, )),

    cryo_g = device('toftof.ccr.DigitalOutput',
                    write = 'cryo_gs',
                    feedback = 'cryo_gr',),

    cryo_vs = device('devices.taco.DigitalOutput',
                    lowlevel = True,
                    tacodevice = '//%s/ccr/plc/vacuum' % (nethost, )),

    cryo_vr= device('devices.taco.DigitalInput',
                    lowlevel = True,
                    tacodevice = '//%s/ccr/plc/fbvacuum' % (nethost, )),

    cryo_v = device('toftof.ccr.DigitalOutput',
                    write = 'cryo_vs',
                    feedback = 'cryo_vr',), 

    cryo_p = device('devices.taco.AnalogInput',
                    tacodevice = '//%s/ccr/plc/p1' % (nethost, )),
)

startupcode = """
T = cryo
Ts = cryo_d
# Ts = cryo_b
SetEnvironment(Ts, T)
"""
