description = 'Closed-cycle cryostat with extension finger'

group = 'plugplay'

includes = ['alias_T']

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'T_%s' % setupname: device('nicos.devices.tango.TemperatureController',
        description = 'The main temperature control',
        tangodevice = tango_base + 'ls/control',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_A' % setupname: device('nicos.devices.tango.Sensor',
        description = 'Sensor A',
        tangodevice = tango_base + 'ls/sensora',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_B' % setupname: device('nicos.devices.tango.Sensor',
        description = 'Sensor B',
        tangodevice = tango_base + 'ls/sensorb',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    'T_%s_range' % setupname: device('nicos.devices.tango.AnalogOutput',
        description = 'The heater range',
        tangodevice = tango_base + 'ls/range',
        fmtstr = '%d',
    ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 200},
    'Ts': {'T_%s_A' % setupname: 100, 'T_%s_B' % setupname: 90},
}
