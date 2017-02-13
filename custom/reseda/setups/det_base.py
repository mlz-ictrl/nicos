#  -*- coding: utf-8 -*-

description = '3He detector'
group = 'lowlevel'

taco_base = '//resedasrv/reseda'

devices = dict(
    timer = device('devices.taco.FRMTimerChannel',
        description = 'Timer channel 2',
        tacodevice = '%s/frmctr/dev0' % taco_base,
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    monitor1 = device('devices.taco.FRMCounterChannel',
        description = 'Monitor channel 1',
        tacodevice = '%s/frmctr/dev1' % taco_base,
        type = 'monitor',
        fmtstr = '%d',
        lowlevel = True,
    ),
    monitor2 = device('devices.taco.FRMCounterChannel',
        description = 'Monitor channel 2',
        tacodevice = '%s/frmctr/dev2' % taco_base,
        type = 'monitor',
        fmtstr = '%d',
        lowlevel = True,
    ),
    counter = device('devices.taco.FRMCounterChannel',
        description = 'Counter channel 1',
        tacodevice = '%s/frmctr/dev3' % taco_base,
        type = 'counter',
        fmtstr = '%d',
        lowlevel = True,
    ),
)
