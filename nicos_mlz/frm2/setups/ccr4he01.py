description = 'FRM II CCR4HE rack with LakeShore LS336 controller and gashanling'
group = 'plugplay'
includes = ['alias_T']


# setupname is set by nicos before loading this file
# setupname = filename - '.py' extension
tango_base = f'tango://{setupname}:10000/box/'
plc_tango_base = tango_base + 'plc/_'


devices = {
    # temperature (control) devices
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
        description = 'Heater range of the sample (stick) regulation',
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
        description = 'Heater range of the tube regulation',
        tangodevice = tango_base + 'tube/range1',
        mapping = dict(off=0, low=1, medium=2, high=3),
    ),
    f'T_{setupname}_sample': device('nicos.devices.entangle.Sensor',
        description = '(optional) Sample temperature',
        tangodevice = tango_base + 'sample/sensora',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_coldhead': device('nicos.devices.entangle.Sensor',
        description = 'Temperature of the coldhead',
        tangodevice = tango_base + 'coldhead/sensorc',
        warnlimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    # coldhead
    f'{setupname}_coldhead': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Compressor for Coldhead (should be ON)',
        tangodevice = plc_tango_base + 'coldhead',
        mapping = {'on': 1, 'off': 0},
    ),
    f'{setupname}_coldhead_ophours': device('nicos.devices.entangle.AnalogInput',
        description = 'coldhead compressor operation hours',
        tangodevice = plc_tango_base + 'coldhead_ophours',
        unit = 'h',
        fmtstr = '%.3f',
    ),
    f'{setupname}_coldhead_p_return': device('nicos.devices.entangle.AnalogInput',
        description = 'coldhead compressor return pressure',
        tangodevice = plc_tango_base + 'coldhead_p1',
        warnlimits = (14, 25),
        unit = 'bar',
        fmtstr = '%.3f',
    ),
    f'{setupname}_coldhead_compressor_temp': device('nicos.devices.entangle.AnalogInput',
        description = 'coldhead compressor temperature',
        tangodevice = plc_tango_base + 'coldhead_t1',
        warnlimits = (0, 80),
        unit = 'C',
        fmtstr = '%.3f',
    ),
    f'{setupname}_coldhead_water_out_temp': device('nicos.devices.entangle.AnalogInput',
        description = 'coldhead compressor water outlet temperature',
        tangodevice = plc_tango_base + 'coldhead_t2',
        warnlimits = (5, 45),
        unit = 'C',
        fmtstr = '%.3f',
    ),
    f'{setupname}_coldhead_water_in_temp': device('nicos.devices.entangle.AnalogInput',
        description = 'coldhead compressor water inlet temperature',
        tangodevice = plc_tango_base + 'coldhead_t3',
        warnlimits = (5, 26),
        unit = 'C',
        fmtstr = '%.3f',
    ),
    # sample tube valves
    f'{setupname}_gas_switch': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Switch for the gas valve',
        tangodevice = plc_tango_base + 'v_gas',
        mapping = {'open': 1, 'closed': 0},
    ),
    f'{setupname}_vacuum_switch': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Switch for the vacuum valve',
        tangodevice = plc_tango_base + 'v_vac',
        mapping = {'open': 1, 'closed': 0},
    ),
    # pressure sensors
    f'{setupname}_p_tube': device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure in sample space',
        tangodevice = plc_tango_base + 'p1',
        fmtstr = '%.3g',
        unit = 'mbar',
    ),
    f'{setupname}_p_still': device('nicos.devices.entangle.AnalogInput',
        description = '1K-Pot pressure',
        tangodevice = plc_tango_base + 'p2',
        fmtstr = '%.3g',
        unit = 'mbar',
    ),
    f'{setupname}_p_cond': device('nicos.devices.entangle.AnalogInput',
        description = 'condense pressure',
        tangodevice = tango_base + 'alicat/pressure',
        fmtstr = '%.3g',
        unit = 'bar',
    ),
    # gashandling read only devices
    f'{setupname}_v1': device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Valve 1 of gashandling system',
        tangodevice = plc_tango_base + 'v1',
        mapping = {'open': 1, 'closed': 0},
    ),
    f'{setupname}_v2': device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Valve 2 of gashandling system',
        tangodevice = plc_tango_base + 'v2',
        mapping = {'open': 1, 'closed': 0},
    ),
    f'{setupname}_v3': device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Valve 3 of gashandling system',
        tangodevice = plc_tango_base + 'v3',
        mapping = {'open': 1, 'closed': 0},
    ),
    f'{setupname}_prepump': device('nicos.devices.entangle.NamedDigitalInput',
        description = 'prepump of gashandling system',
        tangodevice = plc_tango_base + 'prepump',
        mapping = {'on': 1, 'off': 0},
    ),
    f'{setupname}_compressor': device('nicos.devices.entangle.NamedDigitalInput',
        description = 'compressor of gashandling system',
        tangodevice = plc_tango_base + 'compressor',
        mapping = {'on': 1, 'off': 0},
    ),

    f'{setupname}_heatswitch': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Heat switch to connect the 1K stage',
        tangodevice = plc_tango_base + 'heatswitch',
        mapping = {'closed': 1, 'open': 0},
    ),
}


alias_config = {
    'T':  {f'T_{setupname}': 200, f'T_{setupname}_stick': 150, f'T_{setupname}_tube': 100},
    'Ts': {f'T_{setupname}_sample': 100, f'T_{setupname}_stick': 90, f'T_{setupname}_tube': 20, f'T_{setupname}_coldhead': 10},
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
            Field(dev=f'T_{setupname}_tube', name='Regulation'),
            Field(dev=f'T_{setupname}_stick', name='Sample'),
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
            Field(dev=f'{setupname}_p_tube', name='P Tube'),
            Field(dev=f'{setupname}_p_still', name='P Still'),
            Field(dev=f'{setupname}_p_cond', name='P Cond'),
        ),
    ], setups=setupname),
    plots = Block(setupname, [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  plotwindow=300, width=25, height=25,
                  devices=[f'T_{setupname}/setpoint',
                           f'T_{setupname}_coldhead',
                           f'T_{setupname}_still',
                           f'T_{setupname}_tube'],
                  names=['Setpoint', 'Coldhead', 'Regulation', 'Sample'],
                  ),
        ),
    ], setups=setupname)
)


extended = dict(
    representative = f'T_{setupname}',
)
