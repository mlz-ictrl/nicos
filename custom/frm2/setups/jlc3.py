description = 'JCNS CCR box with LakeShore LS336 controller'

group = 'plugplay'

includes = ['alias_T']

# setupname is set by nicos before loading this file
# setupname = filename - '.py' extension
nethost = setupname

devices = {
    'T_%s' % setupname : device('nicos_mlz.frm2.ccr.CCRControl',
                                description = 'The main temperature control device of the ccr',
                                stick = 'T_%s_stick' % setupname,
                                tube = 'T_%s_tube' % setupname,
                                unit = 'K',
                                fmtstr = '%.3f',
                                pollinterval = 5,
                                maxage = 6,
                               ),

    'T_%s_stick' % setupname : device('nicos.devices.taco.TemperatureController',
                                      description = 'The control device of the sample(stick)',
                                      tacodevice = '//%s/ccr/stick/control1' % nethost,
                                      abslimits = (0, 700),
                                      unit = 'K',
                                      fmtstr = '%.3f',
                                      pollinterval = 5,
                                      maxage = 6,
                                     ),

    'T_%s_tube' % setupname : device('nicos.devices.taco.TemperatureController',
                                     description = 'The control device of the tube',
                                     tacodevice = '//%s/ccr/tube/control2' % nethost,
                                     abslimits = (0, 350),
                                     warnlimits = (0, 320),
                                     unit = 'K',
                                     fmtstr = '%.3f',
                                     pollinterval = 5,
                                     maxage = 6,
                                    ),

    'T_%s_A' % setupname : device('nicos.devices.taco.TemperatureSensor',
                                  description = '(optional) Sample Temperature',
                                  tacodevice = '//%s/ccr/sample/sensora' % nethost,
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                  pollinterval = 5,
                                  maxage = 6,
                                 ),

    'T_%s_B' % setupname : device('nicos.devices.taco.TemperatureSensor',
                                  description = '(regulation) Secondary Sample Temperature',
                                  tacodevice = '//%s/ccr/stick/sensorb' % nethost,
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                  pollinterval = 5,
                                  maxage = 6,
                                 ),

    'p_%s' % setupname : device('nicos.devices.taco.TemperatureSensor',
                                  description = 'Pressure in sample tube',
                                  tacodevice = '//%s/ccr/coldhead/sensorc' % nethost,
                                  unit = 'mbar',
                                  fmtstr = '%.3f',
                                  pollinterval = 5,
                                  maxage = 6,
                                 ),

    'T_%s_D' % setupname : device('nicos.devices.taco.TemperatureSensor',
                                  description = '(regulation) Temperature at thermal coupling to the stick',
                                  tacodevice = '//%s/ccr/tube/sensord' % nethost,
                                  warnlimits = (0, 300),
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                  pollinterval = 5,
                                  maxage = 6,
                                 ),

    '%s_gas_switch' % setupname : device('nicos.devices.taco.DigitalOutput',
                                         description = 'Switch for the gas valve',
                                         lowlevel = False,
                                         tacodevice = '//%s/ccr/plc/gas' % nethost,
                                        ),

    '%s_vacuum_switch' % setupname : device('nicos.devices.taco.DigitalOutput',
                                            description = 'Switch for the vacuum valve',
                                            lowlevel = False,
                                            tacodevice = '//%s/ccr/plc/vacuum' % nethost,
                                           ),
}

alias_config = {
    'T':  {'T_%s_tube' % setupname: 200, 'T_%s_stick' % setupname: 150},
    'Ts': {'T_%s_A' % setupname: 100, 'T_%s_B' % setupname: 90, 'T_%s_D' % setupname: 20},
}
