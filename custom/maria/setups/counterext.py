# -*- coding: utf-8 -*-

description = "ZEA-2 counter card setup"
group = "optional"

tango_base = "tango://phys.maria.frm2:10000/maria/"
tango_counter = tango_base + "count/"

devices = dict(
    mon2   = device("jcns.fpga.FPGACounterChannel",
                    description = "Monitor 2",
                    tangodevice = tango_base + 'count/0',
                    type = 'monitor',
                    fmtstr = '%d',
                    channel = 2,
                   ),
    mon3   = device("jcns.fpga.FPGACounterChannel",
                    description = "Monitor 3",
                    tangodevice = tango_base + 'count/0',
                    type = 'monitor',
                    fmtstr = '%d',
                    channel = 3,
                   ),
    mon4   = device("jcns.fpga.FPGACounterChannel",
                    description = "Monitor 4",
                    tangodevice = tango_base + 'count/0',
                    type = 'monitor',
                    fmtstr = '%d',
                    channel = 4,
                   ),
)
