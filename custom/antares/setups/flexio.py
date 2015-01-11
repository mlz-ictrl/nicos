# -*- coding: utf-8 -*-

description = 'ANTARES flexible I/Os'

group = 'optional'

includes = []

tango_host = 'tango://cpci01.antares.frm2:10000'

devices = dict(

    # power sockets / Steckdosen
    FlexOutput = device('devices.tango.DigitalOutput',
                        description = '16bit Flex Output',
                        tangodevice = '%s/antares/fzjdp/FlexOutput' % tango_host,
                       ),
    FlexInput = device('devices.tango.DigitalInput',
                       description = '16bit Flex Input',
                       tangodevice = '%s/antares/fzjdp/FlexInput' % tango_host,
                      ),
)


startupcode = '''
'''
