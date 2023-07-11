description = 'FRM II CCR box with LakeShore LS336 controller'

group = 'plugplay'

includes = ['alias_T']

# setupname is set by nicos before loading this file
# setupname = filename - '.py' extension
tango_base = f'tango://{setupname}:10000/box/'
plc_tango_base = tango_base + 'plc/_'

# This box is equipped with the 1K heatswitch
devices = {
    f'T_{setupname}': device('nicos_mlz.devices.ccr.CCRControl',
        description = 'The main temperature control device of the CCR',
        stick = f'T_{setupname}_stick',
        tube = f'T_{setupname}_tube',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_stick': device('nicos.devices.entangle.TemperatureController',
        description = 'The control device of the sample (stick)',
        tangodevice = tango_base + 'stick/control2',
        abslimits = (0, 600),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_stick_range': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Heaterrange of the sample (stick) regulation',
        tangodevice = tango_base + 'stick/range2',
        mapping = dict(off=0, low=1, medium=2, high=3),
    ),
    f'T_{setupname}_tube': device('nicos.devices.entangle.TemperatureController',
        description = 'The control device of the tube',
        tangodevice = tango_base + 'tube/control1',
        abslimits = (0, 300),
        warnlimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_tube_range': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Heaterrange of the tube regulation',
        tangodevice = tango_base + 'tube/range1',
        mapping = dict(off=0, low=1, medium=2, high=3),
    ),
    f'T_{setupname}_still': device('nicos.devices.entangle.Sensor',
        description = '(LS-Sensor A) Still temperature',
        tangodevice = tango_base + 'sample/sensora',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_sample_stick': device('nicos.devices.entangle.Sensor',
        description = '(LS-Sensor B) Temperature at the stick',
        tangodevice = tango_base + 'stick/sensorb',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_coldhead': device('nicos.devices.entangle.Sensor',
        description = '(LS-Sensor C) Temperature of the coldhead',
        tangodevice = tango_base + 'coldhead/sensorc',
        warnlimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_sample_tube': device('nicos.devices.entangle.Sensor',
        description = '(LS-Sensor D) Temperature at thermal coupling to the tube',
        tangodevice = tango_base + 'tube/sensord',
        warnlimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'{setupname}_compressor': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Compressor for Coldhead (should be ON)',
        tangodevice = plc_tango_base + 'cooler_onoff',
        mapping = {'on': 1, 'off': 0},
    ),
    f'{setupname}_gas_switch': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Switch for the gas valve',
        tangodevice = plc_tango_base + 'gas_onoff',
        mapping = {'on': 1, 'off': 0},
    ),
    f'{setupname}_vacuum_switch': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Switch for the vacuum valve',
        tangodevice = plc_tango_base + 'vacuum_onoff',
        mapping = {'on': 1, 'off': 0},
    ),
    f'{setupname}_p1': device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure in sample space',
        tangodevice = plc_tango_base + 'p1',
        fmtstr = '%.3g',
        unit = 'mbar',
    ),
    f'{setupname}_p2': device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure in the vacuum chamber',
        tangodevice = plc_tango_base + 'p2',
        fmtstr = '%.3g',
        unit = 'mbar',
    ),
    f'{setupname}_pressure_regulate': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'selects pressure regulation',
        tangodevice = plc_tango_base + 'automatik',
        mapping = dict(off = 0, p1 = 1, p2 = 2),
    ),
    f'{setupname}_p1_limits': device('nicos_mlz.devices.plc.ccr.PLCLimits',
        description = 'Limits for Pressure regulation on Channel 1',
        tangodevice = plc_tango_base + 'p1',
        unit = 'mbar',
    ),
    f'{setupname}_p2_limits': device('nicos_mlz.devices.plc.ccr.PLCLimits',
        description = 'Limits for Pressure regulation on Channel 2',
        tangodevice = plc_tango_base + 'p2',
        unit = 'mbar',
    ),
    f'{setupname}_1K_heatswitch': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Heat switch to connect the 1K stage',
        tangodevice = plc_tango_base + 'heatswitch_onoff',
        mapping = {'on': 1, 'off': 0},
    ),
}

alias_config = {
    'T':  {f'T_{setupname}': 200, f'T_{setupname}_stick': 150, f'T_{setupname}_tube': 100},
    'Ts': {f'T_{setupname}_sample_stick': 100, f'T_{setupname}_sample_tube': 90,
           f'T_{setupname}_still': 20, f'T_{setupname}_coldhead': 10},
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

monitor_blocks = dict(
    default = Block('Cryo ' + setupname, [
        BlockRow(
            Field(key=f't_{setupname}/setpoint', unitkey=f't_{setupname}/unit',
                  name='Setpoint', width=12),
            Field(key=f't_{setupname}/target', unitkey=f't_{setupname}/unit',
                  name='Target', width=12),
        ),
        BlockRow(
            Field(dev=f'T_{setupname}_coldhead', name='Coldhead'),
            Field(dev=f'T_{setupname}_still', name='Still'),
            Field(dev=f'T_{setupname}_sample_tube', name='Regulation'),
            Field(dev=f'T_{setupname}_sample_stick', name='Sample'),
        ),
        BlockRow(
            Field(name='Manual Heater Power Stick',
                  key=f't_{setupname}_stick/heaterpower', format='%.3f',
                  unitkey='t/unit'),
        ),
        BlockRow(
            Field(name='Manual Heater Power Tube',
                  key=f't_{setupname}_tube/heaterpower', format='%.3f',
                  unitkey='t/unit'),
        ),
        BlockRow(
            Field(key=f't_{setupname}/p', name='P', width=7),
            Field(key=f't_{setupname}/i', name='I', width=7),
            Field(key=f't_{setupname}/d', name='D', width=6),
        ),
        BlockRow(
            Field(dev=f'{setupname}_p1', name='P1'),
            Field(dev=f'{setupname}_p2', name='P2'),
        )
    ], setups=setupname),
    plots = Block(setupname, [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  plotwindow=300, width=25, height=25,
                  devices=[f'T_{setupname}/setpoint',
                           f'T_{setupname}_coldhead',
                           f'T_{setupname}_sample_tube',
                           f'T_{setupname}_sample_stick'],
                  names=['Setpoint', 'Coldhead', 'Regulation', 'Sample'],
                  ),
        ),
    ], setups=setupname)
)
