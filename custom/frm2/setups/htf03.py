description = 'FRM II high temperature furnace'

group = 'plugplay'

includes = ['alias_T']

nethost = setupname

devices = {
    'T_%s' % setupname : device('nicos.devices.taco.TemperatureController',
                                description = 'The sample temperature',
                                tacodevice = '//%s/box/eurotherm/control' % \
                                             nethost,
                                abslimits = (0, 2000),
                                unit = 'C',
                                fmtstr = '%.3f',
                               ),
    '%s_p' % setupname : device('nicos.devices.taco.AnalogInput',
                                description = 'Pressure sensor of the sample space',
                                tacodevice = '//%s/box/htf/pressure' % nethost,
                                fmtstr = '%.2g',
                               ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 100},
    'Ts': {'T_%s' % setupname: 100},
}
