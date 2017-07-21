# -*- coding: utf-8 -*-

description = "ZEA-2 counter card setup"

group = "optional"

includes = []
excludes = ['detector']

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    timer = device("nicos_mlz.jcns.devices.fpga.FPGATimerChannel",
                   description = "ZEA-2 counter card time",
                   tangodevice = tango_base + 'count/0',
                  ),
    mon1 = device("nicos_mlz.jcns.devices.fpga.FPGACounterChannel",
                  description = "ZEA-2 counter card monitor",
                  tangodevice = tango_base + 'count/0',
                  type = 'monitor',
                  channel = 0,
                 ),
    mon2 = device("nicos_mlz.jcns.devices.fpga.FPGACounterChannel",
                  description = "ZEA-2 counter card monitor",
                  tangodevice = tango_base + 'count/0',
                  type = 'monitor',
                  channel = 0,
                 ),
    ctr1 = device("nicos_mlz.jcns.devices.fpga.FPGACounterChannel",
                  description = "ZEA-2 counter card counter",
                  tangodevice = tango_base + 'count/0',
                  type = 'counter',
                  channel = 0,
                 ),

    det   = device('nicos.devices.generic.Detector',
                   description = 'ZEA-2 multichannel counter card',
                   timers = ['timer'],
                   monitors = ['mon1', 'mon2'],
                   counters = ['ctr1'],
                   maxage = 2,
                   pollinterval = 1.0,
                  ),
)
