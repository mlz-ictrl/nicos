description = 'FRM II infra-red furnace'

group = 'plugplay'

includes = ['alias_T']

nethost = setupname

devices = {
    f'T_{setupname}': device('nicos.devices.taco.TemperatureController',
        description = 'The sample temperature',
        tacodevice = f'//{nethost}/irf/eurotherm/control',
        abslimits = (0, 1200),
        unit = 'C',
        fmtstr = '%.3f',
    ),
}

alias_config = {
    'T':  {f'T_{setupname}': 100},
    'Ts': {f'T_{setupname}': 100},
}

extended = dict(
    representative = f'T_{setupname}',
)
