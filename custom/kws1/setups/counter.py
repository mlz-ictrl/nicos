# -*- coding: utf-8 -*-

description = "ZEA-2 counter card setup"
group = "lowlevel"

tango_base = "tango://phys.kws1.frm2:10000/kws1/"

devices = dict(
    timer  = device("jcns.fpga.FPGATimerChannel",
                    description = "Measurement timer channel",
                    tangodevice = tango_base + 'count/0',
                    extmask = 1 << 3,
                   ),
    mon1   = device("jcns.fpga.FPGACounterChannel",
                    description = "Monitor 1",   # XXX position
                    tangodevice = tango_base + 'count/0',
                    type = 'monitor',
                    fmtstr = '%d',
                    channel = 1,
                    extmask = 1 << 3,
                   ),
    mon2   = device("jcns.fpga.FPGACounterChannel",
                    description = "Monitor 2",   # XXX position
                    tangodevice = tango_base + 'count/0',
                    type = 'monitor',
                    fmtstr = '%d',
                    channel = 2,
                    extmask = 1 << 3,
                   ),
    mon3   = device("jcns.fpga.FPGACounterChannel",
                    description = "Monitor 3",   # XXX position
                    tangodevice = tango_base + 'count/0',
                    type = 'monitor',
                    fmtstr = '%d',
                    channel = 3,
                    extmask = 1 << 3,
                   ),
    selctr = device("jcns.fpga.FPGACounterChannel",
                    description = "Selector rotation counter",
                    tangodevice = tango_base + 'count/0',
                    type = 'counter',
                    fmtstr = '%d',
                    channel = 0,
                    extmask = 1 << 3,
                   ),
    freq   = device("jcns.fpga.FPGAFrequencyChannel",
                    description = "Counter card frequency input",
                    tangodevice = tango_base + 'count/0',
                    extmask = 1 << 3,
                   ),
)
