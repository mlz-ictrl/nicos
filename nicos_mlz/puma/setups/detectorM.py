#  -*- coding: utf-8 -*-

description = 'single detector'

excludes = ['detector']

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    timer = device('nicos.devices.taco.FRMTimerChannel',
        tacodevice = '//%s/puma/qmesydaq/timer' % nethost,
        lowlevel = True,
    ),
    mon1 = device('nicos.devices.taco.FRMCounterChannel',
        tacodevice = '//%s/puma/qmesydaq/counter0' % nethost,
        type = 'monitor',
        lowlevel = True,
        fmtstr = '%d',
    ),
#    mon2 = device('nicos.devices.taco.FRMCounterChannel',
#        tacodevice = '//%s/puma/frmctr/a2' % nethost,
#        type = 'monitor',
#        lowlevel = True,
#        fmtstr = '%d',
#    ),
    det1 = device('nicos.devices.taco.FRMCounterChannel',
        tacodevice = '//%s/puma/qmesydaq/counter1' % nethost,
        type = 'counter',
        lowlevel = True,
        fmtstr = '%d',
    ),
    det2 = device('nicos.devices.taco.FRMCounterChannel',
        tacodevice = '//%s/puma/qmesydaq/counter2' % nethost,
        type = 'counter',
        lowlevel = True,
        fmtstr = '%d',
    ),
    det3 = device('nicos.devices.taco.FRMCounterChannel',
        tacodevice = '//%s/puma/qmesydaq/counter3' % nethost,
        type = 'counter',
        lowlevel = True,
        fmtstr = '%d',
    ),
#    det4 = device('nicos.devices.taco.FRMCounterChannel',
#        tacodevice = '//%s/puma/frmctr/b2' % nethost,
#        type = 'counter',
#        lowlevel = True,
#        fmtstr = '%d',
#    ),

#    det5 = device('nicos.devices.taco.FRMCounterChannel',
#        tacodevice = '//%s/puma/frmctr/b3' % nethost,
#        type = 'counter',
#        lowlevel = True,
#        fmtstr = '%d',
#    ),
    det = device('nicos.devices.generic.Detector',
        description = 'Puma detector QMesydaq device (3 counters)',
        timers = ['timer'],
        monitors = ['mon1'],
        counters = ['det1', 'det2', 'det3'],
        maxage = 1,
        pollinterval = 1,
    ),
)

startupcode = '''
SetDetectors(det)
'''
