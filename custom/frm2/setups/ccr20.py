description = 'FRM II CCR box with LakeShore LS336 controller'

group = 'plugplay'

includes = ['alias_T']

plc_tango_base = 'tango://%s:10000/box/plc/_' % setupname
tango_base = 'tango://%s:10000/box/' % setupname

# This box is equipped with the pressure regulation!
devices = {
    'T_%s' % setupname : device('nicos_mlz.frm2.ccr.CCRControl',
                                description = 'The main temperature control '
                                              'device of the CCR',
                                stick = 'T_%s_stick' % setupname,
                                tube = 'T_%s_tube' % setupname,
                                unit = 'K',
                                fmtstr = '%.3f',
                               ),

    'T_%s_stick' % setupname : device('nicos.devices.tango.TemperatureController',
                                      description = 'The control device of '
                                                    'the sample (stick)',
                                      tangodevice = tango_base + 'stick/control2',
                                      abslimits = (0, 600),
                                      unit = 'K',
                                      fmtstr = '%.3f',
                                     ),

    'T_%s_tube' % setupname : device('nicos.devices.tango.TemperatureController',
                                     description = 'The control device of the '
                                                   'tube',
                                     tangodevice = tango_base + 'tube/control1',
                                     abslimits = (0, 300),
                                     warnlimits = (0, 300),
                                     unit = 'K',
                                     fmtstr = '%.3f',
                                    ),

    'T_%s_stick_range' % setupname : device('nicos.devices.tango.NamedDigitalOutput',
                                     description = 'Heater range',
                                     tangodevice = tango_base + 'stick/range2',
                                     warnlimits = ('high', 'medium'),
                                     mapping = {'off': 0, 'low': 1, 'medium': 2, 'high': 3},
                                     unit = '',
                                    ),

    'T_%s_tube_range' % setupname : device('nicos.devices.tango.NamedDigitalOutput',
                                     description = 'Heater range',
                                     tangodevice = tango_base + 'tube/range1',
                                     warnlimits = ('high', 'medium'),
                                     mapping = {'off': 0, 'low': 1, 'medium': 2, 'high': 3},
                                     unit = '',
                                    ),

    'T_%s_tube' % setupname : device('nicos.devices.tango.TemperatureController',
                                     description = 'The control device of the '
                                                   'tube',
                                     tangodevice = tango_base + 'tube/control1',
                                     abslimits = (0, 300),
                                     warnlimits = (0, 300),
                                     unit = 'K',
                                     fmtstr = '%.3f',
                                    ),

    'T_%s_A' % setupname : device('nicos.devices.tango.Sensor',
                                  description = '(optional) Sample temperature',
                                  tangodevice = tango_base + 'sample/sensora',
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                 ),

    'T_%s_B' % setupname : device('nicos.devices.tango.Sensor',
                                  description = '(regulation) Temperature at '
                                                'the stick',
                                  tangodevice = tango_base + 'stick/sensorb',
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                 ),

    'T_%s_C' % setupname : device('nicos.devices.tango.Sensor',
                                  description = 'Temperature of the coldhead',
                                  tangodevice = tango_base + 'coldhead/sensorc',
                                  warnlimits = (0, 300),
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                 ),

    'T_%s_D' % setupname : device('nicos.devices.tango.Sensor',
                                  description = '(regulation) Temperature at '
                                                'thermal coupling to the tube',
                                  tangodevice = tango_base + 'tube/sensord',
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

    '%s_p1_limits' % setupname : device('nicos_mlz.frm2.ccr.PLCLimits',
                                        description = 'Limits for Pressure regulation on Channel 1',
                                        tangodevice = plc_tango_base + 'p1',
                                        unit = 'mbar',
                                       ),

    '%s_p2_limits' % setupname : device('nicos_mlz.frm2.ccr.PLCLimits',
                                        description = 'Limits for Pressure regulation on Channel 2',
                                        tangodevice = plc_tango_base + 'p2',
                                        unit = 'mbar',
                                       ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 200, 'T_%s_stick' % setupname: 150, 'T_%s_tube' % setupname: 100},
    'Ts': {'T_%s_B' % setupname: 100, 'T_%s_A' % setupname: 90, 'T_%s_D' % setupname: 20, 'T_%s_C' % setupname: 10},
}

startupcode = '''
printinfo("===== %s =====")
printinfo("Please set T_%s.regulationmode to either 'stick', 'tube', or 'both' "
          "according to your needs.")
printinfo("If using the pressure regulation feature, set the limits via "
          "%s_p2_limits or %s_p1_limits.")
printinfo("Activate the wanted channel with the %s_pressure_regulate device or "
          "switch it to 'off' to deactivate the regulation.")
''' % (setupname, setupname, setupname, setupname, setupname)
