# -*- coding: utf-8 -*-

description = 'Hexapod control via TCP/IP'
group = 'optional'
display_order = 70

excludes = ['hexapod_inixlib']

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'
hexapod = tango_base + 'hexapod/h_'

devices = dict(
    hexapod_dt = device('nicos_mlz.jcns.devices.hexapod.Motor',
        description = 'Hexapod rotation table',
        tangodevice = hexapod + 'omega',
        unit = 'deg',
        fmtstr = '%.2f',
    ),
    hexapod_rx = device('nicos_mlz.jcns.devices.hexapod.Motor',
        description = 'Hexapod rotation around X',
        tangodevice = hexapod + 'rx',
        unit = 'deg',
        fmtstr = '%.2f',
    ),
    hexapod_ry = device('nicos_mlz.jcns.devices.hexapod.Motor',
        description = 'Hexapod rotation around Y',
        tangodevice = hexapod + 'ry',
        unit = 'deg',
        fmtstr = '%.2f',
    ),
    hexapod_rz = device('nicos_mlz.jcns.devices.hexapod.Motor',
        description = 'Hexapod rotation around Z',
        tangodevice = hexapod + 'rz',
        unit = 'deg',
        fmtstr = '%.2f',
    ),
    hexapod_tx = device('nicos_mlz.jcns.devices.hexapod.Motor',
        description = 'Hexapod translation in X',
        tangodevice = hexapod + 'tx',
        unit = 'mm',
        fmtstr = '%.1f',
    ),
    hexapod_ty = device('nicos_mlz.jcns.devices.hexapod.Motor',
        description = 'Hexapod translation in Y',
        tangodevice = hexapod + 'ty',
        unit = 'mm',
        fmtstr = '%.1f',
    ),
    hexapod_tz = device('nicos_mlz.jcns.devices.hexapod.Motor',
        description = 'Hexapod translation in Z',
        tangodevice = hexapod + 'tz',
        unit = 'mm',
        fmtstr = '%.1f',
    ),
)
