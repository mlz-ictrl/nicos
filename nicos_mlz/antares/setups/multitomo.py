description = 'Multi tomo setup with four motors in Experimental Chamber 1, currently only 3 motors implemented'

group = 'optional'

devices = dict(
    sry_multi_1 = device('nicos.devices.taco.Motor',
        description = 'Multitomo sample rotation 1',
        tacodevice = 'antares/copley/m01',
        abslimits = (-400, 400),
    ),
    sry_multi_2 = device('nicos.devices.taco.Motor',
        description = 'Multitomo sample rotation 2',
        tacodevice = 'antares/copley/m02',
        abslimits = (-400, 400),
    ),
    sry_multi_3 = device('nicos.devices.taco.Motor',
        description = 'Multitomo sample rotation 3',
        tacodevice = 'antares/copley/m03',
        abslimits = (-400, 400),
    ),
    # sry_multi_4 = device('nicos.devices.taco.Motor',
    #               description = 'Multitomo sample rotation 4',
    #               tacodevice = 'antares/copley/m04',
    #               abslimits = (-400, 400),
    #              ),
)
