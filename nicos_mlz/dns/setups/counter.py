# -*- coding: utf-8 -*-

description = 'ZEA-2 counter card setup'
group = 'optional'

tango_base = 'tango://phys.dns.frm2:10000/dns/'

devices = dict(
    timer = device('nicos_mlz.jcns.devices.fpga_new.FPGATimerChannel',
        description = 'Acquisition time',
        tangodevice = tango_base + 'count/timer',
    ),
    mon1 = device('nicos.devices.tango.CounterChannel',
        description = 'Beam monitor counter',
        tangodevice = tango_base + 'count/mon1',
        type = 'monitor',
    ),
    chopctr = device('nicos.devices.tango.CounterChannel',
        description = 'Chopper zero signal counter',
        tangodevice = tango_base + 'count/chopper',
        type = 'other',
    ),
)

extended = dict(
    representative = 'timer',
)
