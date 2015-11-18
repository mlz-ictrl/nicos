# -*- coding: utf-8 -*-

description = 'ANTARES flexible I/Os'

group = 'optional'

includes = []

tango_host = 'tango://slow.antares.frm2:10000'

devices = dict(

    # power sockets / Steckdosen
    # FlexOutput = device('antares.DigitalOutput',
                        # description = '16bit Flex Output',
                        # tangodevice = '%s/antares/FZJDP_Digital/FlexOutput' % tango_host,
                       # ),
    # FlexInput = device('antares.DigitalInput',
                       # description = '16bit Flex Input',
                       # tangodevice = '%s/antares/FZJDP_Digital/FlexInput' % tango_host,
                      # ),
    FlexOut01 = device('antares.partialdio.PartialDigitalOutput',
                        description = '16bit Flex Output',
                        tangodevice = '%s/antares/FZJDP_Digital/FlexOutput' % tango_host,
                        startbit = 0,
                        bitwidth = 1,
                       ),
    FlexOut02 = device('antares.partialdio.PartialDigitalOutput',
                        description = '16bit Flex Output',
                        tangodevice = '%s/antares/FZJDP_Digital/FlexOutput' % tango_host,
                        startbit = 1,
                        bitwidth = 1,
                       ),
    FlexOut03 = device('antares.partialdio.PartialDigitalOutput',
                        description = '16bit Flex Output',
                        tangodevice = '%s/antares/FZJDP_Digital/FlexOutput' % tango_host,
                        startbit = 2,
                        bitwidth = 1,
                       ),
    FlexOut04 = device('antares.partialdio.PartialDigitalOutput',
                        description = '16bit Flex Output',
                        tangodevice = '%s/antares/FZJDP_Digital/FlexOutput' % tango_host,
                        startbit = 3,
                        bitwidth = 1,
                       ),
)


startupcode = '''
'''
