#  -*- coding: utf-8 -*-

name = 'minimal NICOS startup setup'
group = 'lowlevel'

includes = ['detector']

sysconfig = dict(
    cache = 'localhost',
)

devices = dict(
    outp    = device('antares.i7000.Output',
                     tacodevice='//localhost/test/rs232/dev0',
                     address=2,
                     fmtstr='0x%x'),
    shutter = device('devices.generic.Switcher',
                     moveable='outp',
                     mapping={'open': 1, 'closed': 0},
                     precision=0),
    freq    = device('antares.picotest.G5100A',
                     device='/dev/usbtmc0',
                     unit='Hz', abslimits=(0, 1000000)),
    det     = device('antares.andor.AndorDetector',
                     tacodevice='//localhost/test/andor/dev0'),
)
