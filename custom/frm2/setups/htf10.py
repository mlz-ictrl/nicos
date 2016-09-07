description = 'FRM II high temperature furnace'

group = 'plugplay'

includes = ['alias_T']

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'T_%s' % setupname: device('devices.tango.TemperatureController',
                               description = 'The sample temperature',
                               tangodevice = tango_base + 'eurotherm/ctrl',
                               abslimits = (0, 2000),
                               precision = 0.1,
                               fmtstr = '%.3f',
                               unit = 'C',
                              ),
    'P_%s' % setupname: device('devices.tango.Sensor',
                               description = 'The furnance pressure',
                               tangodevice = tango_base + 'leybold/pressure',
                               fmtstr = '%.3f',
                               unit = 'mbar',
                              ),
    'watertemp_%s' % setupname: device('devices.tango.Sensor',
                               description = 'Cooling water temperature',
                               tangodevice = tango_base + 'plc/_water_temp',
                               fmtstr = '%.3f',
                               unit = 'C',
                              ),
    'waterflow_%s' % setupname: device('devices.tango.Sensor',
                               description = 'Cooling water flow',
                               tangodevice = tango_base + 'plc/_water_flow',
                               fmtstr = '%.3f',
                               unit = 'l/s',
                              ),
    'pumpstate_%s' % setupname: device('devices.tango.NamedDigitalInput',
                               description = 'State of the turbo pump',
                               tangodevice = tango_base + 'plc/_pumpstate',
                               mapping = {'on': 1, 'off': 0}
                              ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 100},
    'Ts': {'T_%s' % setupname: 100},
}
