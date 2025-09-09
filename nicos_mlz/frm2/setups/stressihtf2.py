description = 'Stressi specific high temperature furnace with cooling down ' \
              'option'

group = 'plugplay'

includes = ['alias_T']

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'T_{setupname}': device('nicos.devices.entangle.TemperatureController',
                               description = 'The sample temperature',
                               tangodevice = tango_base + 'eurotherm/ctrl',
                               # abslimits = (0, 2000),
                               # unit = 'C',
                               fmtstr = '%.1f',
                              ),
    f'T_sample_{setupname}': device('nicos.devices.entangle.Sensor',
                                      description = 'The sample temperature '
                                                    'sensor',
                                      tangodevice = tango_base + 'eurotherm/sensora',
                                      # unit = 'C',
                                      fmtstr = '%.1f',
                                     ),
    'n2': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'N2 valve control',
        tangodevice = tango_base + 'plc/_gas1',
        mapping = {'closed': 0, 'open': 1},
        unit = '',
    ),
    'he': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'He valve control',
        tangodevice = tango_base + 'plc/_gas2',
        mapping = {'closed': 0, 'open': 1},
        unit = '',
    ),
    'lamps': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Halogen lamps control',
        tangodevice = tango_base + 'plc/_onoff',
        mapping = {'off': 0, 'on': 1},
        unit = '',
    ),
    'water': device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Cooling water status',
        tangodevice = tango_base + 'plc/_waterok',
        mapping = {'failed': 0, 'ok': 1},
        unit = '',
    ),
}

alias_config = {
    'T':  {f'T_{setupname}': 100},
    'Ts': {f'T_{setupname}': 100},
}

extended = dict(
    representative = f'T_{setupname}',
)
