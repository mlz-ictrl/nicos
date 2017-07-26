description = 'FRM II infra-red furnace'

group = 'plugplay'

includes = ['alias_T']

nethost = setupname

devices = {
    'T_%s' % setupname: device('nicos.devices.taco.TemperatureController',
                               description = 'The sample temperature',
                               tacodevice = '//%s/irf/eurotherm/control' % nethost,
                               abslimits = (0, 1200),
                               unit = 'C',
                               fmtstr = '%.3f',
                              ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 100},
    'Ts': {'T_%s' % setupname: 100},
}
