# -*- coding: utf-8 -*-

description = 'Cryostat manipulation stage'

group = 'optional'

includes = []

tango_host = 'tango://cpci01.antares.frm2:10000'

devices = dict(
    cty = device('devices.tango.Motor',
                 description = 'Flex Achse 1',
                 tangodevice = '%s/antares/fzjs7/Flex_Achse_1' % tango_host,
                 abslimits = (-500000, 500000),
                 userlimits = (-500000, 500000),
                 unit = 'mm',
                ),

    ctx = device('devices.tango.Motor',
                 description = 'Flex Achse 2',
                 tangodevice = '%s/antares/fzjs7/Flex_Achse_2' % tango_host,
                 abslimits = (-500000, 500000),
                 userlimits = (-500000, 500000),
                 unit = 'mm',
                ),

    cry = device('devices.tango.Motor',
                 description = 'Flex Achse 3',
                 tangodevice = '%s/antares/fzjs7/Flex_Achse_3' % tango_host,
                 abslimits = (0, 360),
                 unit = 'deg',
                ),
)

startupcode = '''
'''
