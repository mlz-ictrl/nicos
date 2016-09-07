description = 'FRM II cryo box with two LakeShore controllers'

group = 'optional'

includes = ['alias_T']

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    T_stick   = device('devices.taco.TemperatureController',
                       description = 'Controller for the sample stick',
                       tacodevice = '//%s/toftof/ls2/control' % nethost,
                       abslimits = (0, 600),
                       unit = 'K',
                       fmtstr = '%.3f',
                       pollinterval = 5,
                       maxage = 6,
                      ),

    T_tube = device('devices.taco.TemperatureController',
                    description = 'Controller for tube of the CCR',
                    tacodevice = '//%s/toftof/ls1/control' % nethost,
                    abslimits = (0, 600),
                    unit = 'K',
                    fmtstr = '%.3f',
                    pollinterval = 5,
                    maxage = 6,
                   ),

    T_A = device('devices.taco.TemperatureSensor',
                 description = 'Temperature of the channel A',
                 tacodevice = '//%s/toftof/ls2/sensora' % nethost,
                 unit = 'K',
                 fmtstr = '%.3f',
                ),

    T_B = device('devices.taco.TemperatureSensor',
                 description = 'Temperature of the channel B',
                 tacodevice = '//%s/toftof/ls2/sensorb' % nethost,
                 unit = 'K',
                 fmtstr = '%.3f',
                ),

    T_C = device('devices.taco.TemperatureSensor',
                 description = 'Temperature of the channel C',
                 tacodevice = '//%s/toftof/ls1/sensora' % nethost,
                 unit = 'K',
                 fmtstr = '%.3f',
                ),

    T_D = device('devices.taco.TemperatureSensor',
                 description = 'Temperature of the channel D',
                 tacodevice = '//%s/toftof/ls1/sensorb' % nethost,
                 unit = 'K',
                 fmtstr = '%.3f',
                ),

    compressor_switch = device('devices.taco.DigitalOutput',
                               description = 'The switch for the compressor',
                               tacodevice = '//%s/toftof/ccr/compressor' % \
                                            nethost,
                              ),

    gas_switch = device('devices.taco.DigitalOutput',
                        description = 'The gas valve of the CCR',
                        tacodevice = '//%s/toftof/ccr/gas' % nethost,
                       ),

    vacuum_switch = device('devices.taco.DigitalOutput',
                           description = 'The vaccuum valve of the CCR',
                           tacodevice = '//%s/toftof/ccr/vacuum' % nethost,
                          ),

    _p2 = device('devices.taco.AnalogInput',
                 description = 'Pressure P2 of the CCR',
                 tacodevice = '//%s/toftof/ccr/p2' % nethost,
                ),
)

alias_config = {
    'T':  {'T_tube': 100, 'T_stick': 90},
    'Ts': {'T_B': 100, 'T_C': 80, 'T_A': 90, 'T_D': 70},
}
