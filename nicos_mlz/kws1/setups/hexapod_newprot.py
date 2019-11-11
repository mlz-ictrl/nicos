# -*- coding: utf-8 -*-

description = 'Hexapod control'
group = 'optional'
display_order = 70

excludes = []

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'
hexapod = tango_base + 'hexapod/_'

devices = dict(
    dt = device('nicos.devices.tango.Motor',
        description = 'Hexapod rotation table',
        tangodevice = hexapod + 'omega',
        unit = 'deg',
        precision = 0.01,
        fmtstr = '%.2f',
    ),
    rx = device('nicos.devices.tango.Motor',
        description = 'Hexapod rotation around X',
        tangodevice = hexapod + 'rx',
        unit = 'deg',
        precision = 0.01,
        fmtstr = '%.2f',
    ),
    ry = device('nicos.devices.tango.Motor',
        description = 'Hexapod rotation around Y',
        tangodevice = hexapod + 'ry',
        unit = 'deg',
        precision = 0.01,
        fmtstr = '%.2f',
    ),
    rz = device('nicos.devices.tango.Motor',
        description = 'Hexapod rotation around Z',
        tangodevice = hexapod + 'rz',
        unit = 'deg',
        precision = 0.01,
        fmtstr = '%.2f',
    ),
    tx = device('nicos.devices.tango.Motor',
        description = 'Hexapod translation in X',
        tangodevice = hexapod + 'tx',
        unit = 'mm',
        precision = 0.1,
        fmtstr = '%.1f',
    ),
    ty = device('nicos.devices.tango.Motor',
        description = 'Hexapod translation in Y',
        tangodevice = hexapod + 'ty',
        unit = 'mm',
        precision = 0.1,
        fmtstr = '%.1f',
    ),
    tz = device('nicos.devices.tango.Motor',
        description = 'Hexapod translation in Z',
        tangodevice = hexapod + 'tz',
        unit = 'mm',
        precision = 0.1,
        fmtstr = '%.1f',
    ),
)
