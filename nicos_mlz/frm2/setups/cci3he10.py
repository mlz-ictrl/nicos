description = '3He insert from FRM II Sample environment group'

group = 'plugplay'

includes = ['alias_T']

plc_tango_base = 'tango://%s:10000/box/plc/_' % setupname
ls_tango_base = 'tango://%s:10000/box/lakeshore/' % setupname


devices = {
    'T_%s_pot' % setupname: device('nicos.devices.entangle.TemperatureController',
        description = 'The control device to the 3He-pot',
        tangodevice = ls_tango_base + 'control',
        abslimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
        pollinterval = 5,
        maxage = 6,
    ),
    'T_%s_pot_heaterrange' % setupname: device('nicos.devices.generic.Switcher',
        description = 'Heater range for 3He-pot',
        moveable = device('nicos.devices.entangle.AnalogOutput',
            tangodevice = ls_tango_base + 'heaterrange',
            description = '',
            visibility = (),
            unit = '',),
        precision = 0.5,
        mapping = {'off': 0, '1 mW': 3, '10 mW': 4, '100 mW': 5},
    ),
    'T_%s_sample' % setupname: device('nicos.devices.entangle.Sensor',
        description = 'The sample temperature (if installed)',
        tangodevice = ls_tango_base + 'sensorb',
        unit = 'K',
        fmtstr = '%.3f',
        pollinterval = 5,
        maxage = 6,
    ),
    'T_%s_sample2' % setupname: device('nicos.devices.entangle.Sensor',
        description = 'The 2(nd) sample temperature (if installed)',
        tangodevice = ls_tango_base + 'sensorc',
        unit = 'K',
        fmtstr = '%.3f',
        pollinterval = 5,
        maxage = 6,
    ),
    '%s_p_pot' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure at 3He-pot, also at turbo-pump inlet',
        tangodevice = plc_tango_base + 'pStill',
        fmtstr = '%.3e',
    ),
    '%s_p_inlet' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure at turbo pump outlet, also at pre-pump inlet',
        tangodevice = plc_tango_base + 'pInlet',
        fmtstr = '%.3g',
    ),
    '%s_p_outlet' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure at compressor inlet, also at pre-pump outlet',
        tangodevice = plc_tango_base + 'pOutlet',
        fmtstr = '%.3g',
    ),
    '%s_p_cond' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Condensing pressure, also at compressor outlet',
        tangodevice = plc_tango_base + 'pKond',
        fmtstr = '%.3g',
    ),
    '%s_p_tank' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure in 3He-gas reservoir',
        tangodevice = plc_tango_base+ 'pTank',
        fmtstr = '%.3g',
    ),
    '%s_p_vac' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure in vacuum dewar',
        tangodevice = plc_tango_base + 'pVacc',
        fmtstr = '%.2e',
    ),
    '%s_p_v15' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure on pumping side of V15',
        tangodevice = plc_tango_base + 'pV15',
        fmtstr = '%.2e',
    ),
    '%s_flow' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Gas flow',
        tangodevice = plc_tango_base + 'flow',
        fmtstr = '%.1f',
        unit = 'ml/min',
    ),
}

alias_config = {
    'T':  {'T_%s_pot' % setupname: 300},
    'Ts': {'T_%s_pot' % setupname: 300, 'T_%s_sample' % setupname: 280},
}

extended = dict(
    representative = 'T_%s_pot' % setupname,
)

monitor_blocks = dict(
    default = Block('3He insert ' + setupname, [
        BlockRow(
            Field(name='Setpoint', key=f't_{setupname}_pot/setpoint',
                  unitkey='t/unit'),
            Field(name='Target', key=f't_{setupname}_pot/target',
                  unitkey='t/unit'),
        ),
        BlockRow(
            Field(name='Pot', dev=f'T_{setupname}_pot'),
            Field(name='Manual Heater Power', key=f't_{setupname}_pot/heaterpower',
                  unitkey='t/unit'),
        ),
        BlockRow(
            Field(name='Sample', dev=f'T_{setupname}_sample'),
            Field(name='Sample2', dev=f'T_{setupname}_sample2'),
        ),
    ], setups=setupname),
    pressures = Block('Pressures ' + setupname, [
        BlockRow(
            Field(dev=f'{setupname}_p_pot', name='Pot', width=10),
            Field(dev=f'{setupname}_p_inlet', name='Inlet', width=10),
        ),
        BlockRow(
            Field(dev=f'{setupname}_p_outlet', name='Outlet', width=10),
            Field(dev=f'{setupname}_p_cond', name='Cond', width=10),
        ),
        BlockRow(
            Field(dev=f'{setupname}_p_tank', name='Tank', width=10),
            Field(dev=f'{setupname}_p_vac', name='Vac', width=10),
        ),
        BlockRow(
            Field(dev=f'{setupname}_flow', name='Flow', width=10),
        ),
    ], setups=setupname),
    plots = Block(setupname, [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  plotwindow=300, width=25, height=25,
                  devices=[f't_{setupname}/setpoint', f't_{setupname}'],
                  names=['Setpoint', 'Regulation'],
                  ),
        ),
    ], setups=setupname)
)
