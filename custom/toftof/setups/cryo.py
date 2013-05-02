description = 'FRM-II cryo box with two LakeShore controllers'

group = 'optional'

includes = ['system', 'alias_T']

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    T_stick   = device('devices.taco.TemperatureController',
                       tacodevice = '//%s/toftof/ls2/control' % (nethost,),
                       abslimits = (0, 600),
                       unit = 'K',
                       fmtstr = '%.3f',
                       pollinterval = 5,
                       maxage = 6,
                      ),

    T_tube = device('devices.taco.TemperatureController',
                    tacodevice = '//%s/toftof/ls1/control' % (nethost,),
                    abslimits = (0, 600),
                    unit = 'K',
                    fmtstr = '%.3f',
                    pollinterval = 5,
                    maxage = 6,
                   ),

    T_A = device('devices.taco.TemperatureSensor',
                 tacodevice = '//%s/toftof/ls2/sensora' % (nethost,),
                 unit = 'K',
                 fmtstr = '%.3f',
                ),

    T_B = device('devices.taco.TemperatureSensor',
                 tacodevice = '//%s/toftof/ls2/sensorb' % (nethost,),
                 unit = 'K',
                 fmtstr = '%.3f',
                ),

    T_C = device('devices.taco.TemperatureSensor',
                 tacodevice = '//%s/toftof/ls1/sensora' % (nethost,),
                 unit = 'K',
                 fmtstr = '%.3f',
                ),

    T_D = device('devices.taco.TemperatureSensor',
                 tacodevice = '//%s/toftof/ls1/sensorb' % (nethost,),
                 unit = 'K',
                 fmtstr = '%.3f',
                ),

    compressor_switch = device('devices.taco.DigitalOutput',
                          tacodevice = '//%s/toftof/ccr/compressor' % (nethost,),
                         ),

    gas_switch = device('devices.taco.DigitalOutput',
                        tacodevice = '//%s/toftof/ccr/gas' % (nethost,),
                       ),

    vacuum_switch = device('devices.taco.DigitalOutput',
                           tacodevice = '//%s/toftof/ccr/vacuum' % (nethost,),
                          ),

    _p2 = device('devices.taco.AnalogInput',
                 tacodevice = '//%s/toftof/ccr/p2' % (nethost,),
                ),
)

startupcode = """
T.alias = T_tube
Ts.alias = T_B
AddEnvironment(T, Ts)
"""
