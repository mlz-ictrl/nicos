description = 'Newport sample stick rotational stage controller'

group = 'plugplay'

includes = ['alias_sth']

tango_base = f'tango://{setupname}:10000/'

devices = {
    f'sth_{setupname}': device('nicos.devices.entangle.MotorAxis',
        description = 'Newport rotation axis',
        tangodevice = tango_base + 'box/newport/motor',
        fmtstr = '%.3f',
        unit = 'deg',
    ),
}

alias_config = {
    'sth': {f'sth_{setupname}': 200},
}

extended = dict(
    representative = f'sth_{setupname}',
)
