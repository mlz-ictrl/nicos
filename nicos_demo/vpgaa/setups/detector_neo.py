# -*- coding: utf-8 -*-

description = 'Andor Neo sCMOS camera emulation'

group = 'lowlevel'

devices = dict(
    timer_neo = device('nicos.devices.generic.VirtualTimer',
        description = 'The camera\'s internal timer',
        lowlevel = True,
    ),
    neo = device('nicos.devices.generic.VirtualImage',
        description = 'demo 2D detector',
        fmtstr = '%d',
        sizes = (1024, 1024),
        lowlevel = True,
    ),
    temp_neo = device('nicos.devices.generic.VirtualTemperature',
        description = 'The CMOS chip temperature',
        abslimits = (-100, 0),
        warnlimits = (None, 0),
        speed = 6,
        unit = 'degC',
        maxage = 5,
        fmtstr = '%.0f',
    ),
    det_neo = device('nicos.devices.generic.Detector',
        description = 'The Andor Neo sCMOS camera detector',
        images = ['neo'],
        timers = ['timer_neo'],
    ),
)

startupcode = """
SetDetectors(det_neo)
"""
