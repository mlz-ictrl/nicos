description = 'Philipps Polarizer Setup'

group = 'optional'

includes = []

devices = dict(
    pry = device('nicos.devices.taco.Motor',
        description = 'Polarizer Rotation around Y',
        tacodevice = 'antares/copley/m14',
        abslimits = (-400, 400),
        precision = 0.01,
    ),
    ptx = device('nicos.devices.taco.Motor',
        description = 'Polarizer Translation X',
        tacodevice = 'antares/copley/m15',
        abslimits = (-20, 20),
        precision = 0.01,
    ),
)
