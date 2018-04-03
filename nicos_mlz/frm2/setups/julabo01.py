description = 'Julabo temperature controller'

group = 'plugplay'

includes = ['alias_T']

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'T_%s' % setupname: device('nicos.devices.tango.TemperatureController',
        description = 'The sample temperature',
        tangodevice = tango_base + 'julabo/control',
        abslimits = (-10, 140),
        precision = 0.1,
        fmtstr = '%.2f',
        unit = 'degC',
    ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 200},
    'Ts': {'T_%s' % setupname: 100},
}
