description = 'FRM II CCR box with LakeShore LS336 controller'

group = 'plugplay'

includes = ['alias_T']

# setupname is set by nicos before loading this file
# setupname = filename - '.py' extension
tango_base = f'tango://{setupname}:10000/box/'
plc_tango_base = tango_base + 'plc/_'

devices = {
    f'T_{setupname}': device('nicos_mlz.devices.ccr.CCRControl',
        description = 'The main temperature control device of the CCR (LS-336)',
        stick = f'T_{setupname}_stick',
        tube = f'T_{setupname}_tube',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_stick': device('nicos.devices.entangle.TemperatureController',
        description = 'The control device of the sample (stick) (LS-336)',
        tangodevice = tango_base + 'stick/control2',
        abslimits = (0, 600),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_stick_range': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Heaterrange of the sample (stick) regulation (LS-336)',
        tangodevice = tango_base + 'stick/range2',
        mapping = dict(off=0, low=1, medium=2, high=3),
    ),
    f'T_{setupname}_tube': device('nicos.devices.entangle.TemperatureController',
        description = 'The control device of the tube (LS-336)',
        tangodevice = tango_base + 'tube/control1',
        abslimits = (0, 300),
        warnlimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_tube_range': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Heaterrange of the tube regulation (LS-336)',
        tangodevice = tango_base + 'tube/range1',
        mapping = dict(off=0, low=1, medium=2, high=3),
    ),
    f'T_{setupname}_A': device('nicos.devices.entangle.Sensor',
        description = '(optional) Sample temperature (LS-336)',
        tangodevice = tango_base + 'sample/sensora',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_B': device('nicos.devices.entangle.Sensor',
        description = '(regulation) Temperature at the stick (LS-336)',
        tangodevice = tango_base + 'stick/sensorb',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_C': device('nicos.devices.entangle.Sensor',
        description = 'Temperature of the coldhead (LS-336)',
        tangodevice = tango_base + 'coldhead/sensorc',
        warnlimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_D': device('nicos.devices.entangle.Sensor',
        description = '(regulation) Temperature at thermal coupling to the '
                      'tube (LS-336)',
        tangodevice = tango_base + 'tube/sensord',
        warnlimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_340': device('nicos.devices.entangle.TemperatureController',
        description = 'CCR6 temperature regulation (LS-340)',
        tangodevice = tango_base + 'ls2/control1',
        abslimits = (0, 600),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_340_range': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Heaterrange of the control loop of the LS-340',
        tangodevice = tango_base + 'ls2/range1',
        mapping = dict(off=0, low=1, medium=2, high=3),
    ),

    f'T_{setupname}_A_340': device('nicos.devices.entangle.Sensor',
        description = 'CCR6 sensor A (LS-340)',
        tangodevice = tango_base + 'ls2/sensora',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_B_340': device('nicos.devices.entangle.Sensor',
        description = 'CCR6 sensor B (LS-340)',
        tangodevice = tango_base + 'ls2/sensorb',
        unit = 'K',
        fmtstr = '%.3f',
    ),
}

alias_config = {
    'T': {
        f'T_{setupname}': 200,
        f'T_{setupname}_stick': 150,
        f'T_{setupname}_tube': 100,
        f'T_{setupname}_340': 80
    },
    'Ts': {
        f'T_{setupname}_B': 100,
        f'T_{setupname}_A': 90,
        f'T_{setupname}_D': 20,
        f'T_{setupname}_C': 10,
        f'T_{setupname}_A_340': 8,
        f'T_{setupname}_B_340': 5,
    },
}

startupcode = '''
printinfo("===== %s =====")
printinfo("Please set T_%s.regulationmode to either 'stick', 'tube', or 'both' "
          "according to your needs.")
''' % (setupname, setupname)
