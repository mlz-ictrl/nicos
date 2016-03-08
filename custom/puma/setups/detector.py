#  -*- coding: utf-8 -*-

description = 'single detector'

excludes = ['detectorM']

group = 'lowlevel'

devices = dict(
    timer    = device('devices.taco.FRMTimerChannel',
                      tacodevice = 'puma/frmctr/at',
                      lowlevel = True,
                     ),

    mon1     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/a1',
                      type = 'monitor',
                      lowlevel = True,
                      fmtstr = '%d',
                     ),

    mon2     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/a2',
                      type = 'monitor',
                      lowlevel = True,
                      fmtstr = '%d',
                     ),

    det1     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/a3',
                      type = 'counter',
                      lowlevel = True,
                      fmtstr = '%d',
                     ),

    det2     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/a4',
                      type = 'counter',
                      lowlevel = True,
                      fmtstr = '%d',
                     ),

    det3     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/b1',
                      type = 'counter',
                      lowlevel = True,
                      fmtstr = '%d',
                     ),

    det4     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/b2',
                      type = 'counter',
                      lowlevel = True,
                      fmtstr = '%d',
                     ),

    det5     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/b3',
                      type = 'counter',
                      lowlevel = True,
                      fmtstr = '%d',
                     ),

    det      = device('devices.generic.Detector',
                      description = 'Puma detector device (5 counters)',
                      timers = ['timer'],
                      monitors = ['mon1', 'mon2'],
                      counters = ['det1', 'det2', 'det3', 'det4', 'det5'],
                      maxage = 1,
                      pollinterval = 1,
                     ),
)

startupcode = '''
SetDetectors(det)
'''
