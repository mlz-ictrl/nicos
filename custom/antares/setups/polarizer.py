description = 'Philipps Polarizer Setup'

group = 'optional'

includes = []

devices = dict(
    sry_polarizer = device('devices.taco.Motor',
        description = 'Polarizer Rotation around Y',
        tacodevice = 'antares/copley/m14',
        abslimits = (-999999, 999999),
    ),
    stx_polarizer = device('devices.taco.Motor',
        description = 'Polarizer Translation X',
        tacodevice = 'antares/copley/m15',
        abslimits = (-99999, 99999),
    ),
)
