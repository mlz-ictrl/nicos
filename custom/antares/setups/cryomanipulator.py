# -*- coding: utf-8 -*-

description = 'Cryostat manipulation stage'

group = 'optional'

includes = []

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    cty = device('nicos.devices.tango.Motor',
        description = 'Flex Achse 1',
        tangodevice = tango_base + 'fzjs7/Flex_Achse_1',
        abslimits = (-0, 700),
        userlimits = (-0, 400),
        unit = 'mm',
    ),
    ctx = device('nicos.devices.tango.Motor',
        description = 'Flex Achse 2',
        tangodevice = tango_base + 'fzjs7/Flex_Achse_2',
        abslimits = (-0, 330),
        userlimits = (-0, 330),
        unit = 'mm',
    ),
    cry = device('nicos.devices.tango.Motor',
        description = 'Flex Achse 3',
        tangodevice = tango_base + 'fzjs7/Flex_Achse_3',
        abslimits = (0, 360),
        unit = 'deg',
    ),
)
