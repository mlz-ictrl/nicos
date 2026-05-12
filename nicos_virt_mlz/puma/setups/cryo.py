description = 'virtual temperature device'

group = 'optional'

includes = ['alias_T']

devices = dict(
    T_demo = device('nicos.devices.generic.VirtualRealTemperature',
        description = 'A virtual (but realistic) temperature controller',
        abslimits = (2, 1000),
        warnlimits = (0, 325),
        ramp = 60,
        unit = 'K',
        jitter = 0,
        precision = 0.1,
        window = 30.0,
        visibility = (),
    ),
    T_sample = device('nicos.devices.generic.ReadonlyParamDevice',
        parameter = 'sample',
        device = 'T_demo',
        description = 'Temperature of virtual sample',
        visibility = (),
    ),
    T_setpoint = device('nicos.devices.generic.ParamDevice',
        description = 'Current temperature setpoint',
        device = 'T_demo',
        parameter = 'setpoint',
    )
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

help_topics = {
    'NICOS demo cryo': """
The demo cryostat simulation
############################

The cryo setup enables the access to devices of the (virtual) cryostat.

Some of the devices are used to control the temperature of the cryostat,
whereas others are used to monitor temperatures of the equipment.

The 'T_demo' is a simulation of a cryostat complete with temperature dependent
cooling power, heat-link resistance and specific heat of the simulated sample.

You can play with the 'p', 'i' and 'd' parameters and watch the regulation
behaviour at different temperatures to get a better understanding of how a real
cryostat works.

.. note:

    regulation values are highly specific to the used cryostat, hence the
    values in the simulation are not compatible with those of any real cryostat.
""",
}
