description = 'FRM-II high temperature furnace'

group = 'plugplay'

includes = ['alias_T']

nethost = 'htf05'

devices = {
    'T_%s' % (nethost, ) : device('devices.taco.TemperatureController',
                                  description = 'The sample temperature',
                                  tacodevice = '//%s/htf/eurotherm/control' % \
                                            (nethost, ),
                                  abslimits = (0, 2000),
                                  unit = 'C',
                                  fmtstr = '%.3f',
                                 ),
}

startupcode = """
Ts.alias = T_%s
T.alias = T_%s
AddEnvironment(Ts, T)
""" % (nethost, nethost, )
