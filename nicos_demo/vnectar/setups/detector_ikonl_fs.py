# -*- coding: utf-8 -*-

description = 'Andor IKON-L CCD camera'

group = 'optional'

includes = ['filesavers']
excludes = ['detector', 'detector_ikonl']

devices = dict(
    timer = device('nicos.devices.generic.VirtualTimer',
        description = 'The camera\'s internal timer',
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'The Andor Neo sCMOS camera detector',
        images = ['ccd'],
        timers = ['timer'],
    ),
    ccd = device('nicos.devices.generic.VirtualImage',
        description = 'The CCD detector',
        pollinterval = 5,
        maxage = 12,
        sizes = (1024, 1024),
    ),
    ccdTemp = device('nicos.devices.generic.VirtualTemperature',
        description = 'Temperature of the CCD detector',
        pollinterval = 5,
        maxage = 12,
        abslimits = (-100, 0),
        unit = 'degC',
        precision = 3,
        fmtstr = '%.0f',
    ),
    fov_mot = device('nicos.devices.generic.VirtualMotor',
        description = 'Camera translation x (field of view)',
        abslimits = (0, 900),
        lowlevel = True,
        unit = 'mm',
        speed = 5,
    ),
    fov = device('nicos.devices.generic.Axis',
        description = 'Camera translation x (field of view)',
        pollinterval = 5,
        maxage = 12,
        fmtstr = '%.2f',
        userlimits = (0.0001, 900),
        precision = 0.1,
        motor = 'fov_mot',
    ),
    focus_mot = device('nicos.devices.generic.VirtualMotor',
        description = 'Camera lens roation axis (focus)',
        abslimits = (-100, 100),
        unit = 'deg',
        speed = '5',
        lowlevel = True,
    ),
    focus = device('nicos.devices.generic.Axis',
        description = 'Camera lens roation axis (focus)',
        pollinterval = 5,
        maxage = 12,
        fmtstr = '%.2f',
        userlimits = (-100, 100),
        precision = 0.1,
        motor = 'focus_mot',
    ),
)

startupcode = '''
SetDetectors(det)
'''
