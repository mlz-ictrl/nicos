description = 'Focusing guides translation x'

group = 'optional'

includes = []

devices = dict(
    gtx = device('nicos.devices.taco.Motor',
        description = 'Focusing guides translation x',
        tacodevice = 'antares/copley/m01',
        abslimits = (0, 200),
        precision = 0.01,
    ),
)
