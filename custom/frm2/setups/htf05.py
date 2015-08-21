description = 'FRM-II high temperature furnace'

group = 'plugplay'

includes = ['alias_T']

nethost = setupname

devices = {
    'T_%s' % setupname : device('devices.taco.TemperatureController',
                                description = 'The sample temperature',
                                tacodevice = '//%s/htf/eurotherm/control' % \
                                             nethost,
                                abslimits = (0, 2000),
                                unit = 'C',
                                fmtstr = '%.3f',
                               ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 100},
    'Ts': {'T_%s' % setupname: 100},
}
