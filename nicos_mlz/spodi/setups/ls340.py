description = 'LakeShore LS340 controller'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://spodictrl.spodi.frm2.tum.de:10000/spodi/ls340/'

devices = {
    'T_%s' % setupname : device('nicos.devices.entangle.TemperatureController',
        description = 'The control device of the LS-340',
        tangodevice = tango_base + 'control',
        warnlimits = (0, 300),
        fmtstr = '%.3f',
    ),
    'T_%s_range' % setupname : device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Heater range of the LS-340',
        tangodevice = tango_base + 'range',
        mapping = dict(off=0, low=1, medium=2, high=3),
    ),
    'T_%s_A' % setupname : device('nicos.devices.entangle.Sensor',
        description = 'Temperature channel A',
        tangodevice = tango_base + 'sensora',
        fmtstr = '%.3f',
    ),
    'T_%s_B' % setupname : device('nicos.devices.entangle.Sensor',
        description = 'Temperature channel B',
        tangodevice = tango_base + 'sensorb',
        fmtstr = '%.3f',
    ),
    'T_%s_C' % setupname : device('nicos.devices.entangle.Sensor',
        description = 'Temperature channel C',
        tangodevice = tango_base + 'sensorc',
        fmtstr = '%.3f',
    ),
    'T_%s_D' % setupname : device('nicos.devices.entangle.Sensor',
        description = 'Temperature channel D',
        tangodevice = tango_base + 'sensord',
        fmtstr = '%.3f',
    ),
}

alias_config = {
    'T': {
        'T_%s' % setupname: 200,
    },
    'Ts': {
        'T_%s_B' % setupname: 100,
        'T_%s_A' % setupname: 90,
    },
}
