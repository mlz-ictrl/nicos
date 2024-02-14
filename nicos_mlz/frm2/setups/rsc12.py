description = 'Newport sample stick rotational stage controller'

group = 'plugplay'

includes = ['alias_sth']

tango_base = f'tango://{setupname}:10000/'

devices = {
    f'sth_{setupname}': device('nicos.devices.entangle.MotorAxis',
        description = 'Newport z rotation axis',
        tangodevice = tango_base + 'box/newport/sth',
        fmtstr = '%.3f',
        unit = 'deg',
    ),
    f'sgx_{setupname}': device('nicos.devices.entangle.MotorAxis',
        description = 'Newport x rotation axis',
        tangodevice = tango_base + 'box/newport/sgx',
        fmtstr = '%.3f',
        unit = 'deg',
    ),
    f'stz_{setupname}': device('nicos.devices.entangle.MotorAxis',
        description = 'Newport z translation axis',
        tangodevice = tango_base + 'box/newport/stz',
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

monitor_blocks = dict(
    default = Block(f'RSC {setupname[3:]}', [
        BlockRow(
            Field(name='sth', dev=f'sth_{setupname}', width=12),
        ),
    ], setups=setupname),
)
