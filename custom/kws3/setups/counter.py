# -*- coding: utf-8 -*-

description = "ZEA-2 counter card setup"
group = "lowlevel"
display_order = 15

excludes = ['virtual_daq']

tango_base = "tango://phys.kws3.frm2:10000/kws3/"

devices = dict(
    timer    = device("jcns.fpga.FPGATimerChannel",
                      description = "Measurement timer channel",
                      tangodevice = tango_base + 'count/0',
                      fmtstr = '%.0f',
                      extmask = 1 << 3,
                     ),
    mon1     = device("jcns.fpga.FPGACounterChannel",
                      description = "Monitor 1 (before selector)",
                      tangodevice = tango_base + 'count/0',
                      type = 'monitor',
                      fmtstr = '%d',
                      channel = 1,
                      extmask = 1 << 3,
                      lowlevel = True,
                     ),
    mon2     = device("jcns.fpga.FPGACounterChannel",
                      description = "Monitor 2 (after selector)",
                      tangodevice = tango_base + 'count/0',
                      type = 'monitor',
                      fmtstr = '%d',
                      channel = 2,
                      extmask = 1 << 3,
                      lowlevel = True,
                     ),
    mon1rate = device("jcns.fpga.FPGARate",
                      description = "Instantaneous rate of monitor 1",
                      tangodevice = tango_base + 'count/0',
                      channel = 1,
                      pollinterval = 1.0,
                      fmtstr = '%.1f',
                     ),
    mon2rate = device("jcns.fpga.FPGARate",
                      description = "Instantaneous rate of monitor 2",
                      tangodevice = tango_base + 'count/0',
                      channel = 2,
                      pollinterval = 1.0,
                      fmtstr = '%.1f',
                     ),
)
