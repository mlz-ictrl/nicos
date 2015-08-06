description = 'JCNS cryostream cooler'

group = 'plugplay'

includes = ['alias_T']

tango_host = setupname

devices = {
    'T_%s' % setupname:   device('devices.tango.TemperatureController',
                                 description = 'Sample temperature control',
                                 tangodevice = 'tango://%s:10000/box/cryostream/cryo' % tango_host,
                                 abslimits = (0, 300),
                                 unit = 'K',
                                 fmtstr = '%.3f',
                                 pollinterval = 5,
                                 maxage = 12,
                                ),
    '%s_LN2' % setupname: device('devices.tango.Sensor',
                                 description = 'Cryostream LN2 supply',
                                 tangodevice = 'tango://%s:10000/box/levelmeter/level' % tango_host,
                                 fmtstr = '%.1f',
                                ),
    '%s_LN2_fill' % setupname:
                          device('devices.tango.NamedDigitalOutput',
                                 description = 'Cryostream LN2 supply fill switch',
                                 tangodevice = 'tango://%s:10000/box/levelmeter/fill' % tango_host,
                                 mapping = {'auto': 0, 'fill': 1},
                                ),
}

alias_config = [
    ('T', 'T_%s' % setupname, 100),
    ('Ts', 'T_%s' % setupname, 100),
]
