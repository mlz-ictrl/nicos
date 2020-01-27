# -*- coding: utf-8 -*-

description = 'ZEA-2 counter card setup'
group = 'lowlevel'
display_order = 30

excludes = ['virtual_daq']

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    timer = device('nicos_mlz.jcns.devices.fpga_new.FPGATimerChannel',
        description = 'Measurement timer channel',
        tangodevice = tango_base + 'count/timer',
        fmtstr = '%.0f',
        extmask = 1 << 3,
        exttimeout = 1800,
    ),
    mon1 = device('nicos.devices.tango.CounterChannel',
        description = 'Monitor 1 (before selector)',
        tangodevice = tango_base + 'count/mon1',
        type = 'monitor',
        lowlevel = True,
    ),
    mon2 = device('nicos.devices.tango.CounterChannel',
        description = 'Monitor 2 (after selector)',
        tangodevice = tango_base + 'count/mon2',
        type = 'monitor',
        fmtstr = '%d',
        lowlevel = True,
    ),
    selctr = device('nicos.devices.tango.CounterChannel',
        description = 'Selector rotation counter',
        tangodevice = tango_base + 'count/sel',
        type = 'monitor',
        fmtstr = '%d',
        lowlevel = True,
    ),
    mon1rate = device('nicos.devices.tango.AnalogInput',
        description = 'Instantaneous rate of monitor 1',
        tangodevice = tango_base + 'count/mon1rate',
        pollinterval = 1.0,
        fmtstr = '%.1f',
    ),
    mon2rate = device('nicos.devices.tango.AnalogInput',
        description = 'Instantaneous rate of monitor 2',
        tangodevice = tango_base + 'count/mon2rate',
        pollinterval = 1.0,
        fmtstr = '%.1f',
    ),
)

extended = dict(
    representative = 'timer',
)
