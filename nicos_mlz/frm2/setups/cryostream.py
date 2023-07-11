description = 'JCNS cryostream cooler'

group = 'plugplay'

includes = ['alias_T']

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    'T_cryostream': device('nicos.devices.entangle.TemperatureController',
        description = 'Sample temperature control',
        tangodevice = tango_base + 'cryostream/cryo',
        abslimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
        pollinterval = 5,
        maxage = 12,
    ),
    'cryostream_LN2': device('nicos.devices.entangle.Sensor',
        description = 'Cryostream LN2 supply',
        tangodevice = tango_base + 'levelmeter/level',
        fmtstr = '%.1f',
    ),
    'cryostream_LN2_fill': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Cryostream LN2 supply fill switch',
        tangodevice = tango_base + 'levelmeter/fill',
        mapping = {
            'auto': 0,
            'fill': 1
        },
    ),
}

alias_config = {
    'T':  {'T_cryostream': 100},
    'Ts': {'T_cryostream': 100},
}

extended = dict(
    representative = 'T_cryostream',
)
