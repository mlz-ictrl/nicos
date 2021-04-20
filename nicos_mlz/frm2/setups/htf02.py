description = 'FRM II high temperature furnace'

group = 'plugplay'

includes = ['alias_T']

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'T_%s' % setupname : device('nicos_mlz.devices.htf.HTFTemperatureController',
        description = 'The sample temperature',
        tangodevice = tango_base +'eurotherm/control',
        maxheater = '%s_maxheater' % setupname,
        abslimits = (0, 2000),
        unit = 'C',
        fmtstr = '%.3f',
        precision = 0.1,
    ),
    '%s_p1' % setupname : device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure sensor1 of the sample space',
        tangodevice = tango_base + 'leybold/sensor1',
        fmtstr = '%.3g',
        unit = 'mbar',
    ),
    '%s_p2' % setupname : device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure sensor2 of the sample space',
        tangodevice = tango_base + 'leybold/sensor2',
        fmtstr = '%.3g',
        unit = 'mbar',
    ),
    '%s_p3' % setupname : device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure sensor3 of the sample space',
        tangodevice = tango_base + 'leybold/sensor3',
        fmtstr = '%.3g',
        unit = 'mbar',
    ),
    '%s_maxheater' % setupname: device('nicos.devices.entangle.AnalogOutput',
        description = 'Maximum heater output value for the Eurotherm',
        tangodevice = tango_base + 'eurotherm/maxheateroutput',
        fmtstr = '%.2f',
        unit = '%',
        lowlevel = True,
    ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 100},
    'Ts': {'T_%s' % setupname: 100},
}

extended = dict(
    representative = 'T_%s' % setupname,
)
