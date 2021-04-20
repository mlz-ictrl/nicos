description = 'Stressi specific high temperature furnace'

group = 'plugplay'

includes = ['alias_T']

tango_base = 'tango://%s:10000/box/eurotherm/' % setupname

devices = {
    'T_%s' % setupname: device('nicos.devices.entangle.TemperatureController',
        description = 'The sample temperature',
        tangodevice = tango_base + 'ctrl',
        unit = 'C',
        fmtstr = '%.1f',
    ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 100},
    'Ts': {'T_%s' % setupname: 100},
}
