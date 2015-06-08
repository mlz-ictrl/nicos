description = 'JCNS cryostream cooler'

group = 'plugplay'

includes = ['alias_T']

tango_host = setupname

devices = {
    'T_%s' % setupname:   device('devices.tango.TemperatureController',
                                 description = 'Sample temperature control',
                                 tangodevice = 'tango://' + tango_host + ':10000/box/cryostream/cryo',
                                 abslimits = (0, 300),
                                 unit = 'K',
                                 fmtstr = '%.3f',
                                 pollinterval = 5,
                                 maxage = 12,
                                ),
    '%s_LN2' % setupname: device('devices.tango.Sensor',
                                 description = 'Cryostream LN2 supply',
                                 tangodevice = 'tango://' + tango_host + ':10000/box/levelmeter/level',
                                ),
    '%s_LN2_fill' % setupname:
                          device('devices.tango.NamedDigitalOutput',
                                 description = 'Cryostream LN2 supply fill switch',
                                 tangodevice = 'tango://' + tango_host + ':10000/box/levelmeter/fill',
                                 mapping = {'auto': 0, 'fill': 1},
                                ),
}

startupcode = """
T.alias = T_%s
Ts.alias = T_%s
AddEnvironment(T, Ts)
""" % (setupname, setupname)
