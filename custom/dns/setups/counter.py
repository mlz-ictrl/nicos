# -*- coding: utf-8 -*-

description = "ZEA-2 counter card setup"
group = "optional"

tango_base = 'tango://phys.dns.frm2:10000/dns/'

devices = dict(
    timer = device("nicos_mlz.jcns.devices.fpga.FPGATimerChannel",
                   description = "Acquisition time",
                   tangodevice = tango_base + 'count/0',
                  ),
    mon1  = device("nicos_mlz.jcns.devices.fpga.FPGACounterChannel",
                   description = "Beam monitor counter",
                   tangodevice = tango_base + 'count/0',
                   channel = 0,
                   type = 'monitor',
                  ),
    chopctr = device("nicos_mlz.jcns.devices.fpga.FPGACounterChannel",
                   description = "Chopper zero signal counter",
                   tangodevice = tango_base + 'count/0',
                   channel = 4,
                   type = 'other',
                  ),
)
