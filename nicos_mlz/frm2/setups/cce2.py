description = 'Closed-cycle cryostat with extension finger'

group = 'plugplay'

includes = ['alias_T']

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'T_{setupname}': device('nicos.devices.entangle.TemperatureController',
        description = 'The main temperature control',
        tangodevice = tango_base + 'ls/control',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_A': device('nicos.devices.entangle.Sensor',
        description = 'Sensor A',
        tangodevice = tango_base + 'ls/sensora',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_B': device('nicos.devices.entangle.Sensor',
        description = 'Sensor B',
        tangodevice = tango_base + 'ls/sensorb',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    f'T_{setupname}_range': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'The heater range',
        tangodevice = tango_base + 'ls/range',
        fmtstr = '%d',
        mapping = {'off': 0, 'low': 1, 'medium': 2, 'high': 3},
        unit = '',
    ),
}

alias_config = {
    'T':  {f'T_{setupname}': 200},
    'Ts': {f'T_{setupname}_A': 100, f'T_{setupname}_B': 90},
}

extended = dict(
    representative = f'T_{setupname}',
)
