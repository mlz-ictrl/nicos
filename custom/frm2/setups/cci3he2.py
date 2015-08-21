description = '3He insert from FRM-II Sample environment group'

group = 'plugplay'

includes = ['alias_T']

nethost = setupname

devices = {
    'T_%s' % setupname: device('devices.taco.TemperatureController',
                               description = 'The control device to the 3He pot',
                               tacodevice = '//%s/cryo/ls370/control' % nethost,
                               abslimits = (0, 300),
                               unit = 'K',
                               fmtstr = '%.3f',
                               pollinterval = 5,
                               maxage = 6,
                              ),

    'T_%s_A' % setupname: device('devices.taco.TemperatureSensor',
                                 description = 'The mixing chamber temperature',
                                 tacodevice = '//%s/cryo/ls370/sensora' % nethost,
                                 unit = 'K',
                                 fmtstr = '%.3f',
                                 pollinterval = 5,
                                 maxage = 6,
                                ),

    'T_%s_B' % setupname: device('devices.taco.TemperatureSensor',
                                 description = 'The sample temperature (if installed)',
                                 tacodevice = '//%s/cryo/ls370/sensorb' % nethost,
                                 unit = 'K',
                                 fmtstr = '%.3f',
                                 pollinterval = 5,
                                 maxage = 6,
                                ),

    '%s_p1' % setupname: device('devices.taco.AnalogInput',
                                description = 'Pressure turbo pump inlet',
                                tacodevice = '//%s/cryo/inficon/gauge1' % nethost,
                                fmtstr = '%.4g',
                                pollinterval = 15,
                                maxage = 20,
                               ),

    '%s_p2' % setupname: device('devices.taco.AnalogInput',
                                description = 'Pressure turbo pump outlet',
                                tacodevice = '//%s/cryo/module/gauge2' % nethost,
                                fmtstr = '%.4g',
                                pollinterval = 15,
                                maxage = 20,
                               ),

    '%s_p3' % setupname: device('devices.taco.AnalogInput',
                                description = 'Pressure compressor inlet',
                                tacodevice = '//%s/cryo/module/gauge3' % nethost,
                                fmtstr = '%.4g',
                                pollinterval = 15,
                                maxage = 20,
                               ),

    '%s_p4' % setupname: device('devices.taco.AnalogInput',
                                description = 'Pressure compressor outlet',
                                tacodevice = '//%s/cryo/module/gauge4' % nethost,
                                fmtstr = '%.4g',
                                pollinterval = 15,
                                maxage = 20,
                               ),

    '%s_p5' % setupname: device('devices.taco.AnalogInput',
                                description = 'Pressure dump/tank',
                                tacodevice = '//%s/cryo/module/gauge5' % nethost,
                                fmtstr = '%.4g',
                                pollinterval = 15,
                                maxage = 20,
                               ),

    '%s_p6' % setupname: device('devices.taco.AnalogInput',
                                description = 'Pressure vacuum dewar',
                                tacodevice = '//%s/cryo/inficon/gauge6' % nethost,
                                fmtstr = '%.4g',
                                pollinterval = 15,
                                maxage = 20,
                               ),

    '%s_flow' % setupname: device('devices.taco.AnalogInput',
                                  description = 'Gas flow',
                                  tacodevice = '//%s/cryo/module/flow' % nethost,
                                  fmtstr = '%.4g',
                                  unit = 'mln/min',
                                  pollinterval = 15,
                                  maxage = 20,
                                 ),

}

alias_config = {
    'T':  {'T_%s' % setupname: 300},
    'Ts': {'T_%s_A' % setupname: 300, 'T_%s_B' % setupname: 280},
}
