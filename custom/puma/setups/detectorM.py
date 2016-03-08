#  -*- coding: utf-8 -*-

description = 'single detector'

excludes = ['detector']

group = 'lowlevel'

devices = dict(
    timer    = device('devices.taco.FRMTimerChannel',
                      tacodevice = 'puma/qmesydaq/timer',
                      lowlevel = True,
                     ),

    mon1     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/qmesydaq/counter0',
                      type = 'monitor',
                      lowlevel = True,
                      fmtstr = '%d',
                     ),

#    mon2     = device('devices.taco.FRMCounterChannel',
#                      tacodevice = 'puma/frmctr/a2',
#                      type = 'monitor',
#                      lowlevel = True,
#                      fmtstr = '%d',
#                     ),

    det1     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/qmesydaq/counter1',
                      type = 'counter',
                      lowlevel = True,
                      fmtstr = '%d',
                     ),

    det2     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/qmesydaq/counter2',
                      type = 'counter',
                      lowlevel = True,
                      fmtstr = '%d',
                     ),

    det3     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/qmesydaq/counter3',
                      type = 'counter',
                      lowlevel = True,
                      fmtstr = '%d',
                     ),

#    det4     = device('devices.taco.FRMCounterChannel',
#                      tacodevice = 'puma/frmctr/b2',
#                      type = 'counter',
#                      lowlevel = True,
#                      fmtstr = '%d',
#                     ),

#    det5     = device('devices.taco.FRMCounterChannel',
#                      tacodevice = 'puma/frmctr/b3',
#                      type = 'counter',
#                      lowlevel = True,
#                      fmtstr = '%d',
#                     ),

    det      = device('devices.generic.Detector',
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
