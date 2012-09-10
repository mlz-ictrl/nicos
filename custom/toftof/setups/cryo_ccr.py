description = 'FRM-II CCR box with LakeShore LS336 controller'
includes = ['system']

nethost = 'ccr17.toftof.frm2'

devices = dict(
    cryo   = device('nicos.taco.temperature.TemperatureController',
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

    cryo_tube = device('nicos.taco.temperature.TemperatureController',
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

    cryo_a = device('nicos.taco.TemperatureSensor',
                    tacodevice = '//%s/ccr/ls336/sensora' % (nethost, ),
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_b = device('nicos.taco.TemperatureSensor',
                    tacodevice = '//%s/ccr/ls336/sensorb' % (nethost, ),
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_c = device('nicos.taco.TemperatureSensor',
                    tacodevice = '//%s/ccr/ls336/sensorc' % (nethost, ),
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_d = device('nicos.taco.TemperatureSensor',
                    tacodevice = '//%s/ccr/ls336/sensord' % (nethost, ),
                    unit = 'K',
                    fmtstr = '%g'),

    cryo_machine = device('nicos.taco.DigitalOutput',
                    tacodevice = '//%s/ccr/plc/on' % (nethost, )),

    cryo_gs = device('nicos.taco.DigitalOutput',
                    lowlevel = True,
                    tacodevice = '//%s/ccr/plc/gas' % (nethost, )),

    cryo_gr = device('nicos.taco.DigitalInput',
                    lowlevel = True,
                    tacodevice = '//%s/ccr/plc/fbgas' % (nethost, )),

    cryo_g = device('nicos.toftof.ccr.DigitalOutput',
                    write = 'cryo_gs',
                    feedback = 'cryo_gr',),

    cryo_vs = device('nicos.taco.DigitalOutput',
                    lowlevel = True,
                    tacodevice = '//%s/ccr/plc/vacuum' % (nethost, )),

    cryo_vr= device('nicos.taco.DigitalInput',
                    lowlevel = True,
                    tacodevice = '//%s/ccr/plc/fbvacuum' % (nethost, )),

    cryo_v = device('nicos.toftof.ccr.DigitalOutput',
                    write = 'cryo_vs',
                    feedback = 'cryo_vr',), 

    cryo_p = device('nicos.taco.AnalogInput',
                    tacodevice = '//%s/ccr/plc/p1' % (nethost, )),
)

startupcode = """
T = cryo
Ts = cryo_d
# Ts = cryo_b
SetEnvironment(Ts, T)
"""
