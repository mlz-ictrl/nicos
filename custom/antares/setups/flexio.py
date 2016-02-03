# -*- coding: utf-8 -*-

description = 'ANTARES flexible I/Os'

group = 'optional'

includes = []

tango_host = 'tango://slow.antares.frm2:10000'

devices = dict(

    # FlexOutput = device('antares.DigitalOutput',
                        # description = '16bit Flex Output',
                        # tangodevice = '%s/antares/FZJDP_Digital/FlexOutput' % tango_host,
                       # ),
    # FlexInput = device('antares.DigitalInput',
                       # description = '16bit Flex Input',
                       # tangodevice = '%s/antares/FZJDP_Digital/FlexInput' % tango_host,
                      # ),
    FlexIn01 = device('antares.partialdio.PartialDigitalInput',
                        description = '1bit Flex Input',
                        tangodevice = '%s/antares/FZJDP_Digital/FlexInput' % tango_host,
                        startbit = 0,
                        bitwidth = 1,
                       ),
    FlexIn02 = device('antares.partialdio.PartialDigitalInput',
                        description = '1bit Flex Input',
                        tangodevice = '%s/antares/FZJDP_Digital/FlexInput' % tango_host,
                        startbit = 1,
                        bitwidth = 1,
                       ),
    FlexIn03 = device('antares.partialdio.PartialDigitalInput',
                        description = '1bit Flex Input',
                        tangodevice = '%s/antares/FZJDP_Digital/FlexInput' % tango_host,
                        startbit = 2,
                        bitwidth = 1,
                       ),
    FlexIn04 = device('antares.partialdio.PartialDigitalInput',
                        description = '1bit Flex Input',
                        tangodevice = '%s/antares/FZJDP_Digital/FlexInput' % tango_host,
                        startbit = 3,
                        bitwidth = 1,
                       ),
    FlexOut01 = device('antares.partialdio.PartialDigitalOutput',
                        description = '1bit Flex Output',
                        tangodevice = '%s/antares/FZJDP_Digital/FlexOutput' % tango_host,
                        startbit = 0,
                        bitwidth = 1,
                       ),
    FlexOut02 = device('antares.partialdio.PartialDigitalOutput',
                        description = '1bit Flex Output',
                        tangodevice = '%s/antares/FZJDP_Digital/FlexOutput' % tango_host,
                        startbit = 1,
                        bitwidth = 1,
                       ),
    FlexOut03 = device('antares.partialdio.PartialDigitalOutput',
                        description = '1bit Flex Output',
                        tangodevice = '%s/antares/FZJDP_Digital/FlexOutput' % tango_host,
                        startbit = 2,
                        bitwidth = 1,
                       ),
    FlexOut04 = device('antares.partialdio.PartialDigitalOutput',
                        description = '1bit Flex Output',
                        tangodevice = '%s/antares/FZJDP_Digital/FlexOutput' % tango_host,
                        startbit = 3,
                        bitwidth = 1,
                       ),
)


startupcode = '''
'''
