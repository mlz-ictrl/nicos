#  -*- coding: utf-8 -*-

description = 'detectors'

group = 'lowlevel'

devices = dict(
    timer = device('nicos.devices.taco.FRMTimerChannel',
        tacodevice = '//resictrl/resi/frmctr/at',
        lowlevel = True,
    ),
    mon1 = device('nicos.devices.taco.FRMCounterChannel',
        tacodevice = '//resictrl/resi/frmctr/monitor',
        type = 'monitor',
        lowlevel = True,
    ),
    mon1rate = device('nicos.devices.taco.FRMCounterChannel',
        tacodevice = '//resictrl/resi/frmctr/a4',
        type = 'other',
        lowlevel = True,
    ),
    det1 = device('nicos.devices.taco.FRMCounterChannel',
        tacodevice = '//resictrl/resi/frmctr/counter',
        type = 'counter',
        lowlevel = True,
    ),
    det1rate = device('nicos.devices.taco.FRMCounterChannel',
        tacodevice = '//resictrl/resi/frmctr/a3',
        type = 'other',
        lowlevel = True,
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'combined four channel single counter detector',
        timers = ['timer'],
        monitors = ['mon1'],
        counters = ['det1'],
        maxage = 1,
        pollinterval = 1,
    ),
)

startupcode = '''
SetDetectors(det)
'''
