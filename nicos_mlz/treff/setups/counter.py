# -*- coding: utf-8 -*-

description = "ZEA-2 counter card setup"
group = "lowlevel"

tango_base = "tango://phys.treff.frm2:10000/treff/"

devices = dict(
    timer = device("nicos_mlz.jcns.devices.fpga.FPGATimerChannel",
        description = "ZEA-2 counter card timer channel",
        tangodevice = tango_base + 'count/0',
    ),
    mon0 = device("nicos_mlz.jcns.devices.fpga.FPGACounterChannel",
        description = "Monitor 0",
        tangodevice = tango_base + 'count/0',
        type = 'monitor',
        fmtstr = '%d',
        channel = 0,
    ),
    mon1 = device("nicos_mlz.jcns.devices.fpga.FPGACounterChannel",
        description = "Monitor 1",
        tangodevice = tango_base + 'count/0',
        type = 'monitor',
        fmtstr = '%d',
        channel = 1,
    ),
)
