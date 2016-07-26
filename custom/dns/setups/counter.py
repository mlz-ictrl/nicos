# -*- coding: utf-8 -*-

description = "ZEA-2 counter card setup"
group = "optional"

tango_base = 'tango://phys.dns.frm2:10000/dns/'

devices = dict(
    timer = device("jcns.fpga.FPGATimerChannel",
                   description = "ZEA-2 counter card time",
                   tangodevice = tango_base + 'count/0',
                  ),
    mon1  = device("jcns.fpga.FPGACounterChannel",
                   description = "ZEA-2 counter card monitor",
                   tangodevice = tango_base + 'count/0',
                   channel = 0,
                   type = 'monitor',
                  ),
)
