description = 'FRM II CCR box with LakeShore LS336 controller'

group = 'plugplay'

includes = ['alias_T']

# setupname is set by nicos before loading this file
# setupname = filename - '.py' extension
nethost = setupname

plc_tango_base = 'tango://%s:10000/box/plc/_' % setupname

# This box is equipped with the pressure regulation!
devices = {
    'T_%s' % setupname : device('nicos_mlz.frm2.devices.ccr.CCRControl',
                                description = 'The main temperature control '
                                              'device of the CCR',
                                stick = 'T_%s_stick' % setupname,
                                tube = 'T_%s_tube' % setupname,
                                unit = 'K',
                                fmtstr = '%.3f',
                               ),

    'T_%s_stick' % setupname : device('nicos.devices.taco.TemperatureController',
                                      description = 'The control device of '
                                                    'the sample (stick)',
                                      tacodevice = '//%s/box/stick/control2' % nethost,
                                      abslimits = (0, 600),
                                      unit = 'K',
                                      fmtstr = '%.3f',
                                     ),

    'T_%s_tube' % setupname : device('nicos.devices.taco.TemperatureController',
                                     description = 'The control device of the '
                                                   'tube',
                                     tacodevice = '//%s/box/tube/control1' % nethost,
                                     abslimits = (0, 300),
                                     warnlimits = (0, 300),
                                     unit = 'K',
                                     fmtstr = '%.3f',
                                    ),

    'T_%s_A' % setupname : device('nicos.devices.taco.TemperatureSensor',
                                  description = '(optional) Sample temperature',
                                  tacodevice = '//%s/box/sample/sensora' % nethost,
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                 ),

    'T_%s_B' % setupname : device('nicos.devices.taco.TemperatureSensor',
                                  description = '(regulation) Temperature at '
                                                'the stick',
                                  tacodevice = '//%s/box/stick/sensorb' % nethost,
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                 ),

    'T_%s_C' % setupname : device('nicos.devices.taco.TemperatureSensor',
                                  description = 'Temperature of the coldhead',
                                  tacodevice = '//%s/box/coldhead/sensorc' % nethost,
                                  warnlimits = (0, 300),
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                 ),

    'T_%s_D' % setupname : device('nicos.devices.taco.TemperatureSensor',
                                  description = '(regulation) Temperature at '
                                                'thermal coupling to the tube',
                                  tacodevice = '//%s/box/tube/sensord' % nethost,
                                  warnlimits = (0, 300),
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                 ),

    '%s_compressor' % setupname : device('nicos.devices.tango.NamedDigitalOutput',
                                         description = 'Compressor for Coldhead (should be ON)',
                                         tangodevice = plc_tango_base + 'cooler_onoff',
                                         mapping = {'on' : 1, 'off' : 0},
                                        ),

    '%s_gas_switch' % setupname : device('nicos.devices.tango.NamedDigitalOutput',
                                         description = 'Switch for the gas valve',
                                         tangodevice = plc_tango_base + 'gas_onoff',
                                         mapping = {'on' : 1, 'off' : 0},
                                        ),

    '%s_vacuum_switch' % setupname : device('nicos.devices.tango.NamedDigitalOutput',
                                            description = 'Switch for the vacuum valve',
                                            tangodevice = plc_tango_base + 'vacuum_onoff',
                                            mapping = {'on' : 1, 'off' : 0},
                                           ),

    '%s_p1' % setupname : device('nicos.devices.tango.AnalogInput',
                                 description = 'Pressure in sample space',
                                 tangodevice = plc_tango_base + 'p1',
                                 fmtstr = '%.3g',
                                 unit = 'mbar',
                                ),

    '%s_p2' % setupname : device('nicos.devices.tango.AnalogInput',
                                 description = 'Pressure in the vacuum chamber',
                                 tangodevice = plc_tango_base + 'p2',
                                 fmtstr = '%.3g',
                                 unit = 'mbar',
                                ),

    '%s_pressure_regulate' % setupname : device('nicos.devices.tango.NamedDigitalOutput',
                                                description = "selects pressure regulation",
                                                tangodevice = plc_tango_base + 'automatik',
                                                mapping = dict(off=0, p1=1, p2=2),
                                               ),

    '%s_p1_limits' % setupname : device('nicos_mlz.frm2.devices.ccr.PLCLimits',
                                        description = 'Limits for Pressure regulation on Channel 1',
                                        tangodevice = plc_tango_base + 'p1',
                                        unit = 'mbar',
                                       ),

    '%s_p2_limits' % setupname : device('nicos_mlz.frm2.devices.ccr.PLCLimits',
                                        description = 'Limits for Pressure regulation on Channel 2',
                                        tangodevice = plc_tango_base + 'p2',
                                        unit = 'mbar',
                                       ),
    '%s_1K_heatswitch' % setupname : device('nicos.devices.tango.NamedDigitalOutput',
                                            description = 'Heat switch to connect the 1K stage',
                                            tangodevice = plc_tango_base + 'heatswitch_onoff',
                                            mapping = {'on': 1, 'off': 0},
                                           ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 200, 'T_%s_stick' % setupname: 150, 'T_%s_tube' % setupname: 100},
    'Ts': {'T_%s_B' % setupname: 100, 'T_%s_A' % setupname: 90, 'T_%s_D' % setupname: 20, 'T_%s_C' % setupname: 10},
}

startupcode = '''
printinfo("===== CCR20 =====")
printinfo("Please set T_%s.regulationmode to either 'stick', 'tube', or 'both' "
          "according to your needs.")
printinfo("If using the pressure regulation feature, set the limits via "
          "%s_p2_limits or %s_p1_limits.")
printinfo("Activate the wanted channel with the %s_pressure_regulate device or "
          "switch it to 'off' to deactivate the regulation.")
''' % (setupname, setupname, setupname, setupname)
