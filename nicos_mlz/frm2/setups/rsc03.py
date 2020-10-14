description = 'Newport sample stick rotational stage controller'

group = 'plugplay'

includes = ['alias_sth']

tango_base = 'tango://%s:10000/' % setupname

devices = {
    'sth_%s' % setupname: device('nicos.devices.tango.MotorAxis',
        description = 'Newport rotation axis',
        tangodevice = tango_base + 'box/newport/motor',
        fmtstr = '%.3f',
        unit = 'deg',
    ),
}

alias_config = {
    'sth': {'sth_%s' % setupname: 200},
}

extended = dict(
    representative = 'sth_%s' % setupname,
)
