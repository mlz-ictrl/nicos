description = 'Jcns cryo stream'

group = 'optional'

includes = ['alias_T']

nethost = 'cryostream'

devices = {
    'T_%s' % (nethost,) : device('devices.taco.TemperatureController',
                                 description = 'Sample temperature control',
                                 tacodevice = '//%s/box/occr/control' % (nethost, ),
                                 abslimits = (0, 300),
                                 unit = 'K',
                                 fmtstr = '%.3f',
                                 pollinterval = 5,
                                 maxage = 12,
                                ),

    'T_%s_sens' % (nethost,) : device('devices.taco.TemperatureSensor',
                                      description = 'Sample temperature',
                                      tacodevice = '//%s/box/occr/sensor' % (nethost, ),
                                      unit = 'K',
                                      fmtstr = '%.3f',
                                      pollinterval = 5,
                                      maxage = 12,
                                     ),
}

startupcode = """
T.alias = T_%s
Ts.alias = T_%s_sens
AddEnvironment(T, Ts)
""" % (nethost, nethost, )
