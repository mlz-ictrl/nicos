description = 'FRM-II high temperature furnace'

group = 'optional'

includes = ['alias_T']

nethost = 'htf03'

devices = {
    'T_%s' % (nethost, ) : device('devices.taco.TemperatureController',
                  tacodevice = '//%s/htf/eurotherm/control' % (nethost, ),
                  abslimits = (0, 2000),
                  ramp = 0.1,
                  unit = 'C',
                  fmtstr = '%.3f',
                 ),
}

startupcode = """
Ts.alias = T_%s
T.alias = T_%s
AddEnvironment(Ts, T)
""" % (nethost, nethost, )
