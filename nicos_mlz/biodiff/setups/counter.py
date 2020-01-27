# -*- coding: utf-8 -*-

description = 'ZEA-2 counter card setup'
group = 'optional'

tango_base = 'tango://phys.biodiff.frm2:10000/biodiff/'

devices = dict(
    timer = device('nicos_mlz.jcns.devices.fpga.FPGATimerChannel',
        description = 'ZEA-2 counter card timer channel',
        tangodevice = tango_base + 'count/0',
    ),
    mon1 = device('nicos_mlz.jcns.devices.fpga.FPGACounterChannel',
        description = 'ZEA-2 counter card monitor channel',
        tangodevice = tango_base + 'count/0',
        type = 'monitor',
        channel = 0,
    ),
)
