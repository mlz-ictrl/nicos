description = 'Refsans heater01 stove box'

group = 'plugplay'

includes = ['alias_T']

tango_base = 'tango://%s:10000/box/omega/' % setupname

devices = {
    # 'T_%s' % setupname : device('nicos.devices.entangle.TemperatureController',
    'T_%s' % setupname : device('nicos.devices.entangle.Actuator',
        description = 'Temperature of the stove',
        tangodevice = tango_base + 'temperature',
        abslimits = (0, 400),
        unit = 'degC',
        fmtstr = '%.1f',
    ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 500},
    'Ts':  {'T_%s' % setupname: 500},
}
