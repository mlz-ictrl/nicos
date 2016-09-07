description = 'FRM II infra-red furnace'

group = 'plugplay'

includes = ['alias_T']

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'T_%s' % setupname: device('devices.tango.TemperatureController',
                               description = 'The sample temperature',
                               tangodevice = tango_base + 'eurotherm/ctrl',
                               abslimits = (0, 1200),
                               unit = 'C',
                               fmtstr = '%.3f',
                              ),

    '%s_heatlamp_switch' % setupname: device('devices.tango.NamedDigitalOutput',
                                description = 'Switch for the heat lamps',
                                tangodevice = tango_base + 'plc/_heizlampen',
                                mapping = {'on' : 1, 'off' : 0},
                               ),

    '%s_vacuum_switch' % setupname: device('devices.tango.NamedDigitalOutput',
                                description = 'Switch for the vacuum valve',
                                tangodevice = tango_base + 'plc/_vakuum',
                                mapping = {'on' : 1, 'off' : 0},
                               ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 100},
    'Ts': {'T_%s' % setupname: 100},
}
