group = 'optional'
description = 'virtual temperature device'

devices = dict(
    T = device('nicos.devices.generic.DeviceAlias'),
    Ts = device('nicos.devices.generic.DeviceAlias'),
    T_demo = device('nicos.devices.generic.VirtualRealTemperature',
        description = 'A virtual (but realistic) temperature controller',
        abslimits = (2, 1000),
        warnlimits = (0, 325),
        ramp = 60,
        unit = 'K',
        jitter = 0,
        precision = 0.1,
        window = 30.0,
        lowlevel = True,
    ),
    T_sample = device('nicos.devices.generic.ReadonlyParamDevice',
        parameter = 'sample',
        device = 'T_demo',
        description = 'Temperature of virtual sample',
        lowlevel = True,
    ),
)

alias_config = {
    'T':  {'T_demo': 100},
    'Ts': {'T_sample': 100},
}

extended = dict(
    representative = 'T',
)

watch_conditions = [
    dict(condition = 't_value > 300',
         message = 'Temperature too high (exceeds 300 K)',
         type = 'critical',
         gracetime = 5,
         action = 'maw(T, 290)'),
]

startupcode = """
AddEnvironment(T, Ts)
"""

monitor_blocks = {
    'default': Block('Temperature', [
        BlockRow(Field(gui='nicos_demo/demo/gui/cryo.ui')),
        # BlockRow(Field(dev='T'), Field(key='t/setpoint', name='Setpoint')),
        # BlockRow(Field(dev='T', plot='T', plotwindow=300, width=50),
        #          Field(key='t/setpoint', name='SetP', plot='T', plotwindow=300))
    ], setups=setupname),
}
