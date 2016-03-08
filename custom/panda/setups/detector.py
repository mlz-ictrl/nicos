#  -*- coding: utf-8 -*-

description = 'detectors'

group = 'lowlevel'  # is included by panda.py

includes = []

excludes = ['qmesydaq']

modules = []

devices = dict(
    timer    = device('devices.taco.FRMTimerChannel',
                      tacodevice = 'panda/frmctr/at',
                      lowlevel = True,
                     ),
    mon1     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'panda/frmctr/a1',
                      type = 'monitor',
                      lowlevel = True,
                     ),
    mon2     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'panda/frmctr/a2',
                      type = 'monitor',
                      lowlevel = True,
                     ),
    det1     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'panda/frmctr/a3',
                      type = 'counter',
                      lowlevel = True,
                     ),
    det2     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'panda/frmctr/a4',
                      type = 'counter',
                      lowlevel = True,
                     ),
    det      = device('devices.generic.Detector',
                      description = 'combined four channel single counter detector',
                      timers = ['timer'],
                      monitors = ['mon1', 'mon2'],
                      counters = ['det1', 'det2'],
                      #~ counters = ['det2'],
                      maxage = 1,
                      pollinterval = 1,
                     ),
)

startupcode = '''
SetDetectors(det)
'''
