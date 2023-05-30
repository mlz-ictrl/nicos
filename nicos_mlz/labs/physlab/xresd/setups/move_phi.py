# -*- coding: utf-8 -*-

description = 'phi rotation'
group = 'optional'


tango_base = 'tango://rsxrd.physlab.frm2.tum.de:10000/box/huber/'

devices = dict(
    sam_rot = device('nicos.devices.entangle.Motor',
        description = 'phi rotation',
        tangodevice = tango_base + 'phi',
        unit = 'deg',
        precision = 0.01,
        fmtstr = '%.2f',
    ),
)
