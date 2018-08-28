description = 'Focusing guides translation x'

group = 'optional'

includes = []

devices = dict(
    gtx = device('nicos.devices.taco.Motor',
        description = 'Focusing guides translation x',
        tacodevice = 'antares/copley/m08',
        abslimits = (0, 75),
        precision = 0.01,
    ),
)
