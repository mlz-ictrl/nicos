# -*- coding: utf-8 -*-

description = "ZEA-2 counter card setup"
group = "lowlevel"

excludes = ["virtual_timer"]

tango_base = "tango://phys.maria.frm2:10000/maria/"
tango_counter = tango_base + "count/"

devices = dict(
    timer = device("nicos_mlz.jcns.devices.fpga.FPGATimerChannel",
                   description = "ZEA-2 counter card timer channel",
                   tangodevice = tango_counter + '0',
                  ),
    mon0   = device("nicos_mlz.jcns.devices.fpga.FPGACounterChannel",
                    description = "Monitor 0",  # XXX position
                    tangodevice = tango_base + 'count/0',
                    type = 'monitor',
                    fmtstr = '%d',
                    channel = 0,
                   ),
    mon1   = device("nicos_mlz.jcns.devices.fpga.FPGACounterChannel",
                    description = "Monitor 1",  # XXX position
                    tangodevice = tango_base + 'count/0',
                    type = 'monitor',
                    fmtstr = '%d',
                    channel = 1,
                   ),
)
