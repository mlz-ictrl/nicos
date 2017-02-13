#  -*- coding: utf-8 -*-

description = '3He detector'
group = 'optional'
includes = ['det_base']

taco_base = '//resedasrv/reseda'

devices = dict(
    det = device('devices.generic.Detector',
        description = 'FRM II multichannel counter card',
        timers = ['timer'],
        monitors = ['monitor1', 'monitor2'],
        counters = ['counter'],
        fmtstr = 'timer %s, monitor1 %s, monitor2 %s, ctr %s',
        maxage = 2,
        pollinterval = 0.5,
    ),
    det_rot_mot = device('devices.taco.Motor',
        description = 'Detector rotation (motor)',
        tacodevice = '%s/husco2/motor4' % taco_base,
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    det_rot_enc = device('devices.taco.Coder',
        description = 'Detector rotation (encoder)',
        tacodevice = '%s/enc/det2_1' % taco_base,
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    det_rot = device('devices.generic.Axis',
        description = 'Detector rotation',
        motor = 'det_rot_mot',
        coder = 'det_rot_enc',
        fmtstr = '%.3f',
        precision = 0.1,
    ),
    det_x = device('devices.taco.Motor',
        description = 'Detector x translation (motor)',
        tacodevice = '%s/husco2/motor5' % taco_base,
        fmtstr = '%.3f',
    ),
    det_y = device('devices.taco.Motor',
        description = 'Detector y translation (motor)',
        tacodevice = '%s/husco2/motor6' % taco_base,
        fmtstr = '%.3f',
    ),
)
