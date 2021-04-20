description = 'Multi tomo setup with four motors in Experimental Chamber 1, currently only 3 motors implemented'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2.tum.de:10000/antares/'

devices = dict(
    sry_multi_1 = device('nicos.devices.entangle.Motor',
        description = 'Multitomo sample rotation 1',
        tangodevice = tango_base + 'copley/m01',
        abslimits = (-400, 400),
    ),
    sry_multi_2 = device('nicos.devices.entangle.Motor',
        description = 'Multitomo sample rotation 2',
        tangodevice = tango_base + 'copley/m02',
        abslimits = (-400, 400),
    ),
    sry_multi_3 = device('nicos.devices.entangle.Motor',
        description = 'Multitomo sample rotation 3',
        tangodevice = tango_base + 'copley/m03',
        abslimits = (-400, 400),
    ),
    # sry_multi_4 = device('nicos.devices.entangle.Motor',
    #     description = 'Multitomo sample rotation 4',
    #     tangodevice = tango_base + 'copley/m04',
    #     abslimits = (-400, 400),
    # ),
)
