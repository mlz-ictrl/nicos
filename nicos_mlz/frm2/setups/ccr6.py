description = 'FRM II CCR box with LakeShore LS336 controller'

group = 'plugplay'

includes = ['alias_T']

# setupname is set by nicos before loading this file
# setupname = filename - '.py' extension
tango_base = 'tango://%s:10000/box/' % setupname
plc_tango_base = tango_base + 'plc/_'

devices = {
    'T_%s' % setupname : device('nicos_mlz.devices.ccr.CCRControl',
        description = 'The main temperature control device of the CCR (LS-336)',
        stick = 'T_%s_stick' % setupname,
        tube = 'T_%s_tube' % setupname,
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_stick' % setupname : device('nicos.devices.tango.TemperatureController',
        description = 'The control device of the sample (stick) (LS-336)',
        tangodevice = tango_base + 'stick/control2',
        abslimits = (0, 600),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_stick_range' % setupname : device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Heaterrange of the sample (stick) regulation (LS-336)',
        tangodevice = tango_base + 'stick/range2',
        mapping = dict(off=0, low=1, medium=2, high=3),
    ),
    'T_%s_tube' % setupname : device('nicos.devices.tango.TemperatureController',
        description = 'The control device of the tube (LS-336)',
        tangodevice = tango_base + 'tube/control1',
        abslimits = (0, 300),
        warnlimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_tube_range' % setupname : device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Heaterrange of the tube regulation (LS-336)',
        tangodevice = tango_base + 'tube/range1',
        mapping = dict(off=0, low=1, medium=2, high=3),
    ),
    'T_%s_A' % setupname : device('nicos.devices.tango.Sensor',
        description = '(optional) Sample temperature (LS-336)',
        tangodevice = tango_base + 'sample/sensora',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_B' % setupname : device('nicos.devices.tango.Sensor',
        description = '(regulation) Temperature at the stick (LS-336)',
        tangodevice = tango_base + 'stick/sensorb',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_C' % setupname : device('nicos.devices.tango.Sensor',
        description = 'Temperature of the coldhead (LS-336)',
        tangodevice = tango_base + 'coldhead/sensorc',
        warnlimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_D' % setupname : device('nicos.devices.tango.Sensor',
        description = '(regulation) Temperature at thermal coupling to the '
                      'tube (LS-336)',
        tangodevice = tango_base + 'tube/sensord',
        warnlimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_340' % setupname : device('nicos.devices.tango.TemperatureController',
        description = 'CCR6 temperature regulation (LS-340)',
        tangodevice = tango_base + 'ls2/control1',
        abslimits = (0, 600),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_340_range' % setupname : device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Heaterrange of the control loop of the LS-340',
        tangodevice = tango_base + 'ls2/range1',
        mapping = dict(off=0, low=1, medium=2, high=3),
    ),

    'T_%s_A_340' % setupname : device('nicos.devices.tango.Sensor',
        description = 'CCR6 sensor A (LS-340)',
        tangodevice = tango_base + 'ls2/sensora',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_B_340' % setupname : device('nicos.devices.tango.Sensor',
        description = 'CCR6 sensor B (LS-340)',
        tangodevice = tango_base + 'ls2/sensorb',
        unit = 'K',
        fmtstr = '%.3f',
    ),
}

alias_config = {
    'T': {
        'T_%s' % setupname: 200,
        'T_%s_stick' % setupname: 150,
        'T_%s_tube' % setupname: 100,
        'T_%s_340' % setupname: 80
    },
    'Ts': {
        'T_%s_B' % setupname: 100,
        'T_%s_A' % setupname: 90,
        'T_%s_D' % setupname: 20,
        'T_%s_C' % setupname: 10,
        'T_%s_A_340' % setupname: 8,
        'T_%s_B_340' % setupname: 5,
    },
}

startupcode = '''
printinfo("===== %s =====")
printinfo("Please set T_%s.regulationmode to either 'stick', 'tube', or 'both' "
          "according to your needs.")
''' % (setupname, setupname)
