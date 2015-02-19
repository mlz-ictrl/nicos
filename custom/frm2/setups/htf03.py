description = 'FRM-II high temperature furnace'

group = 'plugplay'

includes = ['alias_T']

nethost = 'htf03'

devices = {
    'T_%s' % (nethost, ) : device('devices.taco.TemperatureController',
                                  description = 'The sample temperature',
                                  tacodevice = '//%s/htf/eurotherm/control' % \
                                            (nethost, ),
                                  abslimits = (0, 2000),
                                  unit = 'C',
                                  fmtstr = '%.3f',
                                 ),
    '%s_p' % (nethost, ) : device('devices.taco.AnalogInput',
                                  description = 'Pressure sensor of the sample space',
                                  tacodevice = '//%s/htf/htf/pressure' % (nethost, ),
                                  fmtstr = '%.2g',
                                 ),
}

startupcode = """
Ts.alias = T_%s
T.alias = T_%s
AddEnvironment(Ts, T)
""" % (nethost, nethost, )
