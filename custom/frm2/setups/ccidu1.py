description = '3He/4He dilution unit from FRM II Sample environment group'

group = 'plugplay'

includes = ['alias_T']

nethost = setupname

devices = {
    'T_%s' % setupname: device('devices.taco.TemperatureController',
                               description = 'The control device to the 3He pot',
                               tacodevice = '//%s/box/ls370/control' % nethost,
                               abslimits = (0, 300),
                               unit = 'K',
                               fmtstr = '%.3f',
                               pollinterval = 5,
                               maxage = 6,
                              ),

    'T_%s_A' % setupname: device('devices.taco.TemperatureSensor',
                                 description = 'The mixing chamber temperature',
                                 tacodevice = '//%s/box/ls370/sensora' % nethost,
                                 unit = 'K',
                                 fmtstr = '%.3f',
                                 pollinterval = 5,
                                 maxage = 6,
                                ),

    'T_%s_B' % setupname: device('devices.taco.TemperatureSensor',
                                 description = 'The sample temperature (if installed)',
                                 tacodevice = '//%s/box/ls370/sensorb' % nethost,
                                 unit = 'K',
                                 fmtstr = '%.3f',
                                 pollinterval = 5,
                                 maxage = 6,
                                ),

    '%s_pStill' % setupname: device('devices.taco.AnalogInput',
                                    description = 'Pressure turbo pump inlet',
                                    tacodevice = '//%s/box/inficon/gauge1' % nethost,
                                    fmtstr = '%.4g',
                                    pollinterval = 15,
                                    maxage = 20,
                                   ),

    '%s_pInlet' % setupname: device('devices.taco.AnalogInput',
                                    description = 'Pressure forepump inlet',
                                    tacodevice = '//%s/box/module/gauge2' % nethost,
                                    fmtstr = '%.4g',
                                    pollinterval = 15,
                                    maxage = 20,
                                   ),

    '%s_pOutlet' % setupname: device('devices.taco.AnalogInput',
                                     description = 'Pressure forepump outlet',
                                     tacodevice = '//%s/box/module/gauge3' % nethost,
                                     fmtstr = '%.4g',
                                     pollinterval = 15,
                                     maxage = 20,
                                   ),

    '%s_pKond' % setupname: device('devices.taco.AnalogInput',
                                   description = 'Pressure compressor outlet',
                                   tacodevice = '//%s/box/module/gauge4' % nethost,
                                   fmtstr = '%.4g',
                                   pollinterval = 15,
                                   maxage = 20,
                                  ),

    '%s_pTank' % setupname: device('devices.taco.AnalogInput',
                                   description = 'Pressure dump/tank',
                                   tacodevice = '//%s/box/module/gauge5' % nethost,
                                   fmtstr = '%.4g',
                                   pollinterval = 15,
                                   maxage = 20,
                                  ),

    '%s_pVac' % setupname: device('devices.taco.AnalogInput',
                                  description = 'Pressure vacuum dewar',
                                  tacodevice = '//%s/box/inficon/gauge6' % nethost,
                                  fmtstr = '%.4g',
                                  pollinterval = 15,
                                  maxage = 20,
                                 ),

    '%s_flow' % setupname: device('devices.taco.AnalogInput',
                                  description = 'Gas flow',
                                  tacodevice = '//%s/box/module/flow' % nethost,
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
