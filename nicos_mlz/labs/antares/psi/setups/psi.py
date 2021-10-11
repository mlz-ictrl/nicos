description = 'Tensile rig together with magnet'

includes = ['doli', 'lambdas', 'pibox01']

devices = dict(
    currentsw = device('nicos.devices.generic.LockedDevice',
        description = 'Polarity switcher',
        device = 'out_1',
        lock = 'I_lambda1',
        unlockvalue = 0,
        fmtstr = '0x%02x',
    ),
    air = device('nicos.devices.generic.DeviceAlias'),
)

alias_config = {
    'air': {'out_0': 100, },
}

# startupcode = '''
# air.alias = 'out_0'
# '''

