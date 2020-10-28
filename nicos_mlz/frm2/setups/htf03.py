description = 'FRM II high temperature furnace'

group = 'plugplay'

includes = ['alias_T']

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'T_%s' % setupname : device('nicos.devices.tango.TemperatureController',
        description = 'The sample temperature',
        tangodevice = tango_base +'eurotherm/control',
        abslimits = (0, 2000),
        unit = 'C',
        fmtstr = '%.3f',
    ),
    '%s_p1' % setupname : device('nicos.devices.tango.AnalogInput',
        description = 'Pressure sensor1 of the sample space',
        tangodevice = tango_base + 'leybold/sensor1',
        fmtstr = '%.3g',
        unit = 'mbar',
    ),
    '%s_p2' % setupname : device('nicos.devices.tango.AnalogInput',
        description = 'Pressure sensor2 of the sample space',
        tangodevice = tango_base + 'leybold/sensor2',
        fmtstr = '%.3g',
        unit = 'mbar',
    ),
    '%s_p3' % setupname : device('nicos.devices.tango.AnalogInput',
        description = 'Pressure sensor3 of the sample space',
        tangodevice = tango_base + 'leybold/sensor3',
        fmtstr = '%.3g',
        unit = 'mbar',
    ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 100},
    'Ts': {'T_%s' % setupname: 100},
}

extended = dict(
    representative = 'T_%s' % setupname,
)
