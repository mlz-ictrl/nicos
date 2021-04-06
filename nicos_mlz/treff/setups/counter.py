# -*- coding: utf-8 -*-

description = "ZEA-2 counter card setup"
group = "lowlevel"

excludes = ["virtual_timer"]

tango_base = "tango://phys.treff.frm2:10000/treff/count/"

devices = dict(
    timer = device("nicos_mlz.jcns.devices.fpga_new.FPGATimerChannel",
        description = "ZEA-2 counter card timer channel",
        tangodevice = tango_base + "timer",
    ),
    mon0 = device("nicos.devices.tango.CounterChannel",
        description = "Monitor 0",  # XXX position
        tangodevice = tango_base + "mon0",
        type = 'monitor',
        fmtstr = '%d',
    ),
    mon1 = device("nicos.devices.tango.CounterChannel",
        description = "Monitor 1",  # XXX position
        tangodevice = tango_base + "mon1",
        type = 'monitor',
        fmtstr = '%d',
    ),
)
