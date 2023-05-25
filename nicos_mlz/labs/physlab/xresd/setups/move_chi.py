# -*- coding: utf-8 -*-

description = 'try to move chi'
group = 'optional'
# display_order = 36

# excludes = ['virtual_sample']

tango_base = 'tango://rsxrd.softlab.frm2.tum.de:10000/box/huber/'

devices = dict(
    sam_tilt = device('nicos.devices.entangle.Motor',
        description = 'sample tilt chi',
        tangodevice = tango_base + 'chi',
        unit = 'deg',
        precision = 0.01,
        fmtstr = '%.2f',
    ),
)

extended = dict(
    representative = 'sam_tilt',
)
