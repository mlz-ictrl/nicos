description = 'FRM II high temperature furnace'

group = 'plugplay'

includes = ['alias_T']

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'T_%s' % setupname: device('nicos.devices.tango.TemperatureController',
        description = 'The sample temperature',
        tangodevice = tango_base + 'eurotherm/ctrl',
        abslimits = (0, 2000),
        precision = 0.1,
        fmtstr = '%.3f',
        unit = 'C',
    ),
    '%s_vacuum' % setupname: device('nicos.devices.tango.Sensor',
        description = 'The furnace pressure',
        tangodevice = tango_base + 'leybold/pressure',
        fmtstr = '%.3f',
        unit = 'mbar',
    ),
    '%s_watertemp' % setupname: device('nicos.devices.tango.Sensor',
        description = 'Cooling water temperature',
        tangodevice = tango_base + 'plc/_water_temp',
        fmtstr = '%.3f',
        unit = 'C',
    ),
    '%s_waterflow' % setupname: device('nicos.devices.tango.Sensor',
        description = 'Cooling water flow',
        tangodevice = tango_base + 'plc/_water_flow',
        fmtstr = '%.3f',
        unit = 'l/s',
    ),
    '%s_pumpstate' % setupname: device('nicos.devices.tango.NamedDigitalInput',
        description = 'State of the turbo pump',
        tangodevice = tango_base + 'plc/_pumpstate',
        mapping = {'on': 1, 'off': 0}
    ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 100},
    'Ts': {'T_%s' % setupname: 100},
}
