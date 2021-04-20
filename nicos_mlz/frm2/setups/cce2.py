description = 'Closed-cycle cryostat with extension finger'

group = 'plugplay'

includes = ['alias_T']

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'T_%s' % setupname: device('nicos.devices.entangle.TemperatureController',
        description = 'The main temperature control',
        tangodevice = tango_base + 'ls/control',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_A' % setupname: device('nicos.devices.entangle.Sensor',
        description = 'Sensor A',
        tangodevice = tango_base + 'ls/sensora',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_B' % setupname: device('nicos.devices.entangle.Sensor',
        description = 'Sensor B',
        tangodevice = tango_base + 'ls/sensorb',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_range' % setupname: device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'The heater range',
        tangodevice = tango_base + 'ls/range',
        fmtstr = '%d',
        mapping = {'off': 0, 'low': 1, 'medium': 2, 'high': 3},
        unit = '',
    ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 200},
    'Ts': {'T_%s_A' % setupname: 100, 'T_%s_B' % setupname: 90},
}
