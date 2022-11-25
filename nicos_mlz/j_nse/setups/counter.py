# -*- coding: utf-8 -*-

description = 'ZEA-2 counter card setup'
group = 'lowlevel'

tango_base = 'tango://phys.j-nse.frm2:10000/j-nse/'

devices = dict(
    timer = device('nicos_mlz.jcns.devices.fpga.FPGATimerChannel',
        description = 'Counter card timer channel',
        tangodevice = tango_base + 'count/timer',
    ),
    mon0 = device('nicos.devices.entangle.CounterChannel',
        description = 'Monitor 0',
        tangodevice = tango_base + 'count/mon0',
        type = 'monitor',
    ),
    mon1 = device('nicos.devices.entangle.CounterChannel',
        description = 'Monitor 1',
        tangodevice = tango_base + 'count/mon1',
        type = 'monitor',
    ),
)
