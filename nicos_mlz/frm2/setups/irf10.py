description = 'FRM II infra-red furnace'

group = 'plugplay'

includes = ['alias_T']

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'T_{setupname}': device('nicos.devices.entangle.TemperatureController',
        description = 'The sample temperature',
        tangodevice = tango_base + 'eurotherm/ctrl',
        abslimits = (0, 1200),
        unit = 'C',
        fmtstr = '%.3f',
    ),
    f'{setupname}_maxheater': device('nicos.devices.entangle.AnalogOutput',
        description = 'The maximum heater power',
        tangodevice = tango_base + 'eurotherm/maxheater',
        abslimits = (0, 100),
        unit = '%',
        fmtstr = '%.0f',
    ),
    f'{setupname}_heatlamp_switch': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Switch for the heat lamps',
        tangodevice = tango_base + 'plc/_heizlampen',
        mapping = {'on' : 1, 'off' : 0},
    ),
    f'{setupname}_vacuum_switch': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Switch for the vacuum valve',
        tangodevice = tango_base + 'plc/_vakuum',
        mapping = {'on' : 1, 'off' : 0},
    ),
}

alias_config = {
    'T':  {f'T_{setupname}': 100},
    'Ts': {f'T_{setupname}': 100},
}

extended = dict(
    representative = f'T_{setupname}',
)
