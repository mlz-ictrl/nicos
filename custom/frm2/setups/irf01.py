description = 'FRM-II infra-red furnace'

group = 'plugplay'

includes = ['alias_T']

nethost = 'irf01'

devices = {
    'T_%s' % (nethost, ) : device('devices.taco.TemperatureController',
                                  description = 'The sample temperature',
                                  tacodevice = '//%s/irf/eurotherm/control' % \
                                            (nethost, ),
                                  abslimits = (0, 1200),
                                  unit = 'C',
                                  fmtstr = '%.3f',
                                 ),
}

startupcode = """
Ts.alias = T_%s
T.alias = T_%s
AddEnvironment(Ts, T)
""" % (nethost, nethost, )
