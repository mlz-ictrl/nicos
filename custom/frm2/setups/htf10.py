description = 'FRM-II high temperature furnace'

group = 'plugplay'

includes = ['alias_T']

tango_base = 'tango://%s:10000' % setupname

devices = {
    'T_%s' % setupname : device('devices.tango.TemperatureController',
                                description = 'The sample temperature',
                                tangodevice = '%s/box/eurotherm/ctrl' % \
                                             tango_base,
                                abslimits = (0, 2000),
                                precision = 0.1,
                                fmtstr = '%.3f',
                                unit = 'C',
                               ),
    'P_%s' % setupname : device('devices.tango.Sensor',
                                description = 'The furnance pressure',
                                tangodevice = '%s/box/leybold/pressure' % \
                                             tango_base,
                                fmtstr = '%.3f',
                                unit = 'mbar',
                               ),
    'watertemp_%s' % setupname : device('devices.tango.Sensor',
                                description = 'Cooling water temperature',
                                tangodevice = '%s/box/plc/_water_temp' % \
                                             tango_base,
                                fmtstr = '%.3f',
                                unit = 'C',
                               ),
    'waterflow_%s' % setupname : device('devices.tango.Sensor',
                                description = 'Cooling water flow',
                                tangodevice = '%s/box/plc/_water_flow' % \
                                             tango_base,
                                fmtstr = '%.3f',
                                unit = 'l/s',
                               ),
    'pumpstate_%s' % setupname : device('devices.tango.NamedDigitalInput',
                                description = 'State of the turbo pump',
                                tangodevice = '%s/box/plc/_pumpstate' % \
                                             tango_base,
                                mapping={'on' : 1, 'off' : 0}
                               ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 100},
    'Ts': {'T_%s' % setupname: 100},
}
