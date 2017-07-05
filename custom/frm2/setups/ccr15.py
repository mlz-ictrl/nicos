description = 'FRM II CCR box with LakeShore LS336 controller'

group = 'plugplay'

includes = ['alias_T']

# setupname is set by nicos before loading this file
# setupname = filename - '.py' extension
nethost = setupname

devices = {
    'T_%s' % setupname : device('frm2.ccr.CCRControl',
                                description = 'The main temperature control '
                                              'device of the CCR',
                                stick = 'T_%s_stick' % setupname,
                                tube = 'T_%s_tube' % setupname,
                                unit = 'K',
                                fmtstr = '%.3f',
                                pollinterval = 5,
                                maxage = 6,
                               ),

    'T_%s_stick' % setupname : device('nicos.devices.taco.TemperatureController',
                                      description = 'The control device of '
                                                    'the sample (stick)',
                                      tacodevice = '//%s/ccr/stick/control2' % nethost,
                                      abslimits = (0, 600),
                                      unit = 'K',
                                      fmtstr = '%.3f',
                                      pollinterval = 5,
                                      maxage = 6,
                                     ),

    'T_%s_tube' % setupname : device('nicos.devices.taco.TemperatureController',
                                     description = 'The control device of the '
                                                   'tube',
                                     tacodevice = '//%s/ccr/tube/control1' % nethost,
                                     abslimits = (0, 300),
                                     warnlimits = (0, 300),
                                     unit = 'K',
                                     fmtstr = '%.3f',
                                     pollinterval = 5,
                                     maxage = 6,
                                    ),

    'T_%s_A' % setupname : device('nicos.devices.taco.TemperatureSensor',
                                  description = '(optional) Sample temperature',
                                  tacodevice = '//%s/ccr/sample/sensora' % nethost,
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                  pollinterval = 5,
                                  maxage = 6,
                                 ),

    'T_%s_B' % setupname : device('nicos.devices.taco.TemperatureSensor',
                                  description = '(regulation) Temperature at '
                                                'the stick',
                                  tacodevice = '//%s/ccr/stick/sensorb' % nethost,
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                  pollinterval = 5,
                                  maxage = 6,
                                 ),

    'T_%s_C' % setupname : device('nicos.devices.taco.TemperatureSensor',
                                  description = 'Temperature of the coldhead',
                                  tacodevice = '//%s/ccr/coldhead/sensorc' % nethost,
                                  warnlimits = (0, 300),
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                  pollinterval = 5,
                                  maxage = 6,
                                 ),

    'T_%s_D' % setupname : device('nicos.devices.taco.TemperatureSensor',
                                  description = '(regulation) Temperature at '
                                                'thermal coupling to the tube',
                                  tacodevice = '//%s/ccr/tube/sensord' % nethost,
                                  warnlimits = (0, 300),
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                  pollinterval = 5,
                                  maxage = 6,
                                 ),

    '%s_compressor_switch' % setupname : device('frm2.ccr.CompressorSwitch',
                                                description = 'Switch for the compressor',
                                                tacodevice = '//%s/ccr/plc/on' % nethost,
                                                offdev = '//%s/ccr/plc/off' % nethost,
                                                readback = '//%s/ccr/plc/fbcooler' % nethost,
                                                statusdev = '//%s/ccr/plc/state' % nethost,
                                                mapping = {'on' : 1, 'off' : 0},
                                               ),

    '%s_gas_set' % setupname : device('nicos.devices.taco.DigitalOutput',
                                      description = 'Switch for the gas valve',
                                      lowlevel = True,
                                      tacodevice = '//%s/ccr/plc/gas' % nethost,
                                     ),

    '%s_gas_read' % setupname : device('nicos.devices.taco.DigitalInput',
                                       description = 'Read back of the gas valve state',
                                       lowlevel = True,
                                       tacodevice = '//%s/ccr/plc/fbgas' % nethost,
                                      ),

    '%s_gas_switch' % setupname : device('nicos.devices.vendor.frm2.CCRSwitch',
                                         description = 'Gas valve switch',
                                         write = '%s_gas_set' % setupname,
                                         feedback = '%s_gas_read' % setupname,
                                        ),

    '%s_vacuum_set' % setupname : device('nicos.devices.taco.DigitalOutput',
                                         description = 'Switch for the vacuum'
                                                       'valve',
                                         lowlevel = True,
                                         tacodevice = '//%s/ccr/plc/vacuum' % nethost,
                                        ),

    '%s_vacuum_read' % setupname : device('nicos.devices.taco.DigitalInput',
                                          description = 'Read back of the '
                                                        'vacuum valve state',
                                          lowlevel = True,
                                          tacodevice = '//%s/ccr/plc/fbvacuum' % nethost,
                                         ),

    '%s_vacuum_switch' % setupname : device('nicos.devices.vendor.frm2.CCRSwitch',
                                            description = 'Vacuum valve switch',
                                            write = '%s_vacuum_set' % setupname,
                                            feedback = '%s_vacuum_read' % setupname,
                                           ),

    '%s_p1' % setupname : device('nicos.devices.taco.AnalogInput',
                                 description = 'Pressure in sample space',
                                 tacodevice = '//%s/ccr/plc/p1' % nethost,
                                 fmtstr = '%.4g',
                                 pollinterval = 15,
                                 maxage = 20,
                                 unit = 'mbar',
                                ),

    '%s_p2' % setupname : device('nicos.devices.taco.AnalogInput',
                                 description = 'Pressure in the vacuum chamber',
                                 tacodevice = '//%s/ccr/plc/p2' % nethost,
                                 fmtstr = '%.4g',
                                 pollinterval = 15,
                                 maxage = 20,
                                 unit = 'mbar',
                                ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 200, 'T_%s_stick' % setupname: 150, 'T_%s_tube' % setupname: 100},
    'Ts': {'T_%s_B' % setupname: 100, 'T_%s_A' % setupname: 90, 'T_%s_D' % setupname: 20, 'T_%s_C' % setupname: 10},
}

startupcode = '''
printinfo("Please set T_%s.regulationmode to either 'stick', 'tube', or 'both' "
          "according to your needs.")
''' % setupname
