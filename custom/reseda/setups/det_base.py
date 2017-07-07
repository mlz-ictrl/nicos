#  -*- coding: utf-8 -*-

description = '3He detector'
group = 'lowlevel'

includes = ['filesavers']

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    timer = device('devices.tango.TimerChannel',
        description = 'Timer channel 2',
        tangodevice = '%s/frmctr/timer' % tango_base,
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    monitor1 = device('devices.tango.CounterChannel',
        description = 'Monitor channel 1',
        tangodevice = '%s/frmctr/counter0' % tango_base,
        type = 'monitor',
        fmtstr = '%d',
        lowlevel = True,
    ),
    monitor2 = device('devices.tango.CounterChannel',
        description = 'Monitor channel 2',
        tangodevice = '%s/frmctr/counter1' % tango_base,
        type = 'monitor',
        fmtstr = '%d',
        lowlevel = True,
    ),
    counter = device('devices.tango.CounterChannel',
        description = 'Counter channel 1',
        tangodevice = '%s/frmctr/counter2' % tango_base,
        type = 'counter',
        fmtstr = '%d',
        lowlevel = True,
    ),
)
