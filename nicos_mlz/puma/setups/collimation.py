description = 'PUMA collimator devices'

group = 'optional'

includes = ['motorbus9']

devices = dict(
    alpha4 = device('nicos.devices.generic.ReadonlySwitcher',
        description = 'alpha4 - collimator',
        readable = device('nicos.devices.vendor.ipc.Input',
            bus = 'motorbus9',
            addr = 103,
            first = 8,
            last = 10,
        ),
        mapping = {
            '10': 1,
            '30': 2,
            '45': 3,
            '60': 4,
            '20': 6,
            'PE/120': 7,
        },
        unit = 'min',
        fallback = 'undefined',
   ),
   alpha3 = device('nicos.devices.generic.ReadonlySwitcher',
        description = 'alpha3 - collimator',
        readable = device('nicos.devices.vendor.ipc.Input',
            bus = 'motorbus6',
            addr = 111,
            first = 0,
            last = 2,
        ),
        mapping = {
            '20': 1,
            '10': 2,
            '30': 3,
            '45': 4,
            '60': 6,
            '120': 7,
        },
        unit = 'min',
        fallback = 'undefined',
    ),
)
