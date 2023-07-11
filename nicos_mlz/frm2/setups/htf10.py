description = 'FRM II high temperature furnace'

group = 'plugplay'

includes = ['alias_T']

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'T_{setupname}': device('nicos.devices.entangle.TemperatureController',
        description = 'The sample temperature',
        tangodevice = tango_base + 'eurotherm/ctrl',
        abslimits = (0, 2000),
        precision = 0.1,
        fmtstr = '%.3f',
        unit = 'C',
    ),
    f'{setupname}_vacuum': device('nicos.devices.entangle.Sensor',
        description = 'The furnace pressure',
        tangodevice = tango_base + 'leybold/pressure',
        fmtstr = '%.3f',
        unit = 'mbar',
    ),
    f'{setupname}_watertemp': device('nicos.devices.entangle.Sensor',
        description = 'Cooling water temperature',
        tangodevice = tango_base + 'plc/_water_temp',
        fmtstr = '%.3f',
        unit = 'C',
    ),
    f'{setupname}_waterflow': device('nicos.devices.entangle.Sensor',
        description = 'Cooling water flow',
        tangodevice = tango_base + 'plc/_water_flow',
        fmtstr = '%.3f',
        unit = 'l/s',
    ),
    f'{setupname}_pumpstate': device('nicos.devices.entangle.NamedDigitalInput',
        description = 'State of the turbo pump',
        tangodevice = tango_base + 'plc/_pumpstate',
        mapping = {'on': 1, 'off': 0}
    ),
}

alias_config = {
    'T':  {f'T_{setupname}': 100},
    'Ts': {f'T_{setupname}': 100},
}

extended = dict(
    representative = f'T_{setupname}',
)
