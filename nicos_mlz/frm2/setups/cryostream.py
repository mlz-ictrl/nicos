description = 'JCNS cryostream cooler'

group = 'plugplay'

includes = ['alias_T']

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'T_%s' % setupname:   device('nicos.devices.tango.TemperatureController',
                                 description = 'Sample temperature control',
                                 tangodevice = tango_base + 'cryostream/cryo',
                                 abslimits = (0, 300),
                                 unit = 'K',
                                 fmtstr = '%.3f',
                                 pollinterval = 5,
                                 maxage = 12,
                                ),
    '%s_LN2' % setupname: device('nicos.devices.tango.Sensor',
                                 description = 'Cryostream LN2 supply',
                                 tangodevice = tango_base + 'levelmeter/level',
                                 fmtstr = '%.1f',
                                ),
    '%s_LN2_fill' % setupname:
                          device('nicos.devices.tango.NamedDigitalOutput',
                                 description = 'Cryostream LN2 supply fill switch',
                                 tangodevice = tango_base + 'levelmeter/fill',
                                 mapping = {'auto': 0, 'fill': 1},
                                ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 100},
    'Ts': {'T_%s' % setupname: 100},
}
