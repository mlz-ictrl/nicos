description = 'FRM II LakeShore LS336 controller via entangle server'

group = 'optional'

includes = ['alias_T']

setupname = 'ls336'

tango_base = 'tango://antareshw:10000/ls336/'

# This box is equipped with the pressure regulation!
devices = {
#    'T_%s' % setupname : device('nicos_mlz.devices.ccr.CCRControl',
#        description = 'The main temperature control device of the CCR',
#        stick = 'T_%s_stick' % setupname,
#        tube = 'T_%s_tube' % setupname,
#        unit = 'K',
#        fmtstr = '%.3f',
#    ),
    'T_%s_dose' % setupname : device('nicos.devices.tango.TemperatureController',
        description = 'The control device of the sample',
        tangodevice = tango_base + 'stick/control2',
        abslimits = (0, 600),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_stab' % setupname : device('nicos.devices.tango.TemperatureController',
        description = 'The control device of the tube',
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
        description = '(regulation) Temperature at the stick',
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
        description = '(regulation) Temperature at thermal coupling to the tube',
        tangodevice = tango_base + 'tube/sensord',
        warnlimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
    ),
}

# alias_config = {
#     'T':  {'T_%s' % setupname: 200, 'T_%s_stick' % setupname: 150, 'T_%s_tube' % setupname: 100},
#     'Ts': {'T_%s_B' % setupname: 100, 'T_%s_A' % setupname: 90, 'T_%s_D' % setupname: 20, 'T_%s_C' % setupname: 10},
# }

startupcode = '''
printinfo("===== %s =====")
printinfo("Please set T_%s.regulationmode to either 'stick', 'tube', or 'both' "
          "according to your needs.")
''' % (setupname, setupname)
