# -*- coding: utf-8 -*-

description = 'ANTARES flexible I/Os'

group = 'optional'

includes = []

tango_base = 'tango://slow.antares.frm2:10000/antares/'

devices = dict(

    # power sockets / Steckdosen
    # FlexOutput = device('antares.DigitalOutput',
                        # description = '16bit Flex Output',
                        # tangodevice = tango_base + 'fzjdp_digital/FlexOutput',
                       # ),
    # FlexInput = device('antares.DigitalInput',
                       # description = '16bit Flex Input',
                       # tangodevice = tango_base + 'fzjdp_digital/FlexInput',
                      # ),
    FlexOut01  = device('antares.partialdio.PartialDigitalOutput',
                        description = '16bit Flex Output',
                        tangodevice = tango_base + 'fzjdp_digital/FlexOutput',
                        startbit = 0,
                        bitwidth = 1,
                       ),
    FlexOut02  = device('antares.partialdio.PartialDigitalOutput',
                        description = '16bit Flex Output',
                        tangodevice = tango_base + 'fzjdp_digital/FlexOutput',
                        startbit = 1,
                        bitwidth = 1,
                       ),
    FlexOut03  = device('antares.partialdio.PartialDigitalOutput',
                        description = '16bit Flex Output',
                        tangodevice = tango_base + 'fzjdp_digital/FlexOutput',
                        startbit = 2,
                        bitwidth = 1,
                       ),
    FlexOut04  = device('antares.partialdio.PartialDigitalOutput',
                        description = '16bit Flex Output',
                        tangodevice = tango_base + 'fzjdp_digital/FlexOutput',
                        startbit = 3,
                        bitwidth = 1,
                       ),
)


startupcode = '''
'''
