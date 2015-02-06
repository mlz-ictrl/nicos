# -*- coding: utf-8 -*-

description = "ZEA-2 counter card setup"

group = "optional"

includes = []
excludes = ['detector']

tango_host = 'tango://localhost:10000'

devices = dict(
    timer = device("jcns.fpga.FPGATimerChannel",
                   description = "ZEA-2 counter card time",
                   tangodevice = '%s/poli/count/0' % tango_host,
                  ),
    mon1 = device("jcns.fpga.FPGACounterChannel",
                  description = "ZEA-2 counter card monitor",
                  tangodevice = '%s/poli/count/0' % tango_host,
                  channel = 0,
                 ),
    mon2 = device("jcns.fpga.FPGACounterChannel",
                  description = "ZEA-2 counter card monitor",
                  tangodevice = '%s/poli/count/0' % tango_host,
                  channel = 0,
                 ),
    ctr1 = device("jcns.fpga.FPGACounterChannel",
                  description = "ZEA-2 counter card counter",
                  tangodevice = '%s/poli/count/0' % tango_host,
                  channel = 0,
                 ),

    det   = device('devices.generic.MultiChannelDetector',
                   description = 'ZEA-2 multichannel counter card',
                   timer  = 'timer',
                   monitors = ['mon1', 'mon2'],
                   counters = ['ctr1'],
                   fmtstr = 'timer %s, mon1 %s, mon2 %s, ctr1 %s',
                   maxage = 2,
                   pollinterval = 1.0,
                  ),
)
