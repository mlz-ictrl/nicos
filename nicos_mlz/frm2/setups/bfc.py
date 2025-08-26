description = 'battery furnace control (bfc)'
group = 'plugplay'

includes = ['alias_T']

tango_base = f'tango://{setupname}:10000/box/lakeshore/'

devices = {
    f'T_{setupname}_control_1' : device('nicos.devices.entangle.TemperatureController',
        description = 'BFC temperature regulation A',
        tangodevice = tango_base + 'controla',
        pollinterval = 1,
        maxage = 6,
        abslimits = (0, 500),
    ),
    f'T_{setupname}_control_2' : device('nicos.devices.entangle.TemperatureController',
        description = 'BFC temperature regulation B',
        tangodevice = tango_base + 'controlb',
        pollinterval = 1,
        maxage = 6,
        abslimits = (0, 500),
    ),
    f'T_{setupname}_A' : device('nicos.devices.entangle.AnalogInput',
        description = 'BFC temperature Sensor A',
        tangodevice = tango_base + 'sensora',
        pollinterval = 1,
        maxage = 6,
    ),
    f'T_{setupname}_B' : device('nicos.devices.entangle.AnalogInput',
        description = 'BFC temperature Sensor B',
        tangodevice = tango_base + 'sensorb',
        pollinterval = 1,
        maxage = 6,
    ),
    f'T_{setupname}_C' : device('nicos.devices.entangle.AnalogInput',
        description = 'BFC temperature Sensor C',
        tangodevice = tango_base + 'sensorc',
        pollinterval = 1,
        maxage = 6,
    ),
    f'T_{setupname}_D' : device('nicos.devices.entangle.AnalogInput',
        description = 'BFC temperature Sensor D',
        tangodevice = tango_base + 'sensord',
        pollinterval = 1,
        maxage = 6,
    ),
}

alias_config = {
    'T': {f'T_{setupname}_control_1': 60, f'T_{setupname}_control_2': 50},
    'Ts': {f'T_{setupname}_A': 60, f'T_{setupname}_B': 50,
           f'T_{setupname}_C': 40, f'T_{setupname}_D': 30},
}

extended = dict(
    representative = f'T_{setupname}_A',
)

monitor_blocks = dict(
    default = Block(setupname, [
        BlockRow(
            Field(name='A', dev=f'T_{setupname}_A'),
            Field(name='B', dev=f'T_{setupname}_B'),
            Field(name='C', dev=f'T_{setupname}_C'),
            Field(name='D', dev=f'T_{setupname}_D'),
        ),
        BlockRow(
            Field(name='Setpoint1', key=f't_{setupname}_control_1/setpoint',
                  unitkey=f't_{setupname}_control_1/unit'),
            Field(name='Target1', key=f't_{setupname}_control_1/target',
                  unitkey=f't_{setupname}_control_1/unit'),
            Field(name='Setpoint2', key=f't_{setupname}_control_2/setpoint',
                  unitkey=f't_{setupname}_control_2/unit'),
            Field(name='Target2', key=f't_{setupname}_control_2/target',
                  unitkey=f't_{setupname}_control_2/unit'),
        ),
    ], setups=setupname),
    plots = Block(setupname, [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  plotwindow=300, width=25, height=25,
                  devices=[f't_{setupname}_A', f't_{setupname}_B',
                           f't_{setupname}_C', f't_{setupname}_D',
                           f't_{setupname}_control_1/setpoint',
                           f't_{setupname}_control_1',
                           f't_{setupname}_control_2/setpoint',
                           f't_{setupname}_control_2',
                          ],
                  names=['A', 'B', 'C', 'D',
                         'Setpoint1', 'Regulation1',
                         'Setpoint2', 'Regulation2',
                         ],
                  ),
        ),
    ], setups=setupname)
)
