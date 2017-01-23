#  -*- coding: utf-8 -*-

description = 'detectors'

group = 'lowlevel'  # is included by panda.py

excludes = ['qmesydaq']

tango_base = 'tango://phys.panda.frm2:10000/panda/'

devices = dict(
    timer    = device('devices.tango.TimerChannel',
                      tangodevice = tango_base + 'frmctr2/timer',
                      lowlevel = True,
                     ),
    mon1     = device('devices.tango.CounterChannel',
                      tangodevice = tango_base + 'frmctr2/mon1',
                      type = 'monitor',
                      fmtstr = '%d',
                      lowlevel = True,
                     ),
    mon2     = device('devices.tango.CounterChannel',
                      tangodevice = tango_base + 'frmctr2/mon2',
                      type = 'monitor',
                      fmtstr = '%d',
                      lowlevel = True,
                     ),
    det1     = device('devices.tango.CounterChannel',
                      tangodevice = tango_base + 'frmctr2/det1',
                      type = 'counter',
                      fmtstr = '%d',
                      lowlevel = True,
                     ),
    det2     = device('devices.tango.CounterChannel',
                      tangodevice = tango_base + 'frmctr2/det2',
                      type = 'counter',
                      fmtstr = '%d',
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
