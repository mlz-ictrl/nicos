#  -*- coding: utf-8 -*-

description = '3He detector'

group = 'optional'

includes = ['det_base']
excludes = ['det_cascade']

devices = dict(
    scandet = device('nicos_mlz.reseda.devices.scandet.ScanningDetector',
        description = 'Scanning detector for scans per echotime',
        scandev = 'nse1',
        detector = 'det',
        maxage = 2,
        pollinterval = 0.5,
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'FRM II multichannel counter card',
        timers = ['timer'],
        monitors = ['monitor1'],
        counters = ['counter'],
        fmtstr = 'timer %s, monitor1 %s, ctr %s',
        maxage = 2,
        pollinterval = 0.5,
    ),
    det_hv = device('nicos.devices.generic.VirtualMotor',
        description = 'High voltage power supply of the 3he detector',
        abslimits = (0, 1350),
        unit = 'V',
        curvalue = 0,
    ),
    det_rot_mot = device('nicos.devices.generic.VirtualMotor',
        description = 'Detector rotation (motor)',
        abslimits = (-20, 20),
        fmtstr = '%.3f',
        lowlevel = True,
        unit = 'deg',
    ),
    det_rot = device('nicos.devices.generic.Axis',
        description = 'Detector rotation',
        motor = 'det_rot_mot',
        coder = 'det_rot_enc',
        fmtstr = '%.3f',
        precision = 0.1,
    ),
    det_x = device('nicos.devices.generic.VirtualMotor',
        description = 'Detector x translation (motor)',
        abslimits = (-3, 3),
        fmtstr = '%.1f',
        unit = 'mm',
    ),
    det_y = device('nicos.devices.generic.VirtualMotor',
        description = 'Detector y translation (motor)',
        abslimits = (-3, 3),
        fmtstr = '%.1f',
        unit = 'mm'
    ),
)

startupcode = '''
SetDetectors(det)
'''
