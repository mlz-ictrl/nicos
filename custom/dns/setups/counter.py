# -*- coding: utf-8 -*-

description = "ZEA-2 counter card setup"

group = "optional"

includes = []

tango_host = 'tango://phys.dns.frm2:10000'

devices = dict(
    timer = device("jcns.fpga.FPGATimerChannel",
                   description = "ZEA-2 counter card time",
                   tangodevice = '%s/dns/count/0' % tango_host,
                  ),
    mon0  = device("jcns.fpga.FPGACounterChannel",
                   description = "ZEA-2 counter card monitor",
                   tangodevice = '%s/dns/count/0' % tango_host,
                   channel = 0,
                   type = 'monitor',
                  ),
)
