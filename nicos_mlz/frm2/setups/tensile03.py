description = 'Tensile machine'

group = 'plugplay'

display_order = 40

tango_base = f'tango://{setupname}:10000/test/doli/'

includes = ['alias_te']

devices = {
    f'teload_{setupname}': device('nicos.devices.entangle.Actuator',
        description = 'load value of the tensile machine',
        tangodevice = tango_base + 'load',
        precision = 2,
        fmtstr = '%.1f',
        visibility = (),
    ),
    f'tepos_{setupname}': device('nicos.devices.entangle.Actuator',
        description = 'position value of the tensile machine',
        tangodevice = tango_base + 'position',
        fmtstr = '%.4f',
        visibility = (),
    ),
    f'teext_{setupname}': device('nicos.devices.entangle.Actuator',
        description = 'extension value of the tensile machine',
        tangodevice = tango_base + 'extension',
        fmtstr = '%.3f',
        visibility = (),
    ),
}

alias_config = {
    'teload':  {f'teload_{setupname}': 100},
    'tepos': {f'tepos_{setupname}': 100},
    'teext': {f'teext_{setupname}': 100},
}

monitor_blocks = dict(
    default = Block('Tensile rig ' + setupname, [
        BlockRow(
            Field(dev=f'teload_{setupname}_C', name='Load'),
            Field(dev=f'tepos_{setupname}_D', name='Position'),
            Field(dev=f'teext_{setupname}_B', name='Extension'),
        ),
    ], setups=setupname),
)
