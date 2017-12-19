# -*- coding: utf-8 -*-

description = 'Flexible I/Os'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict()

for bit in range(10):
    indev = device('nicos_mlz.antares.devices.partialdio.PartialDigitalInput',
        description = '1bit Flex Input',
        tangodevice = tango_base + 'fzjdp_digital/FlexInput',
        startbit = bit,
    )
    outdev = device('nicos_mlz.antares.devices.partialdio.PartialDigitalOutput',
        description = '1bit Flex Output',
        tangodevice = tango_base + 'fzjdp_digital/FlexOutput',
        startbit = bit,
    )
    devices['FlexIn%02d' % (bit + 1)] = indev
    devices['FlexOut%02d' % (bit + 1)] = outdev
