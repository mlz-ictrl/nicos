# -*- coding: utf-8 -*-

description = 'Sample tilt table'
group = 'optional'
display_order = 36

excludes = ['virtual_sample']

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'

devices = dict(
    sam_tilt = device('nicos.devices.tango.Motor',
        description = 'sample tilt',
        tangodevice = tango_base + 'fzjs7/sample_axis_tilt',
        unit = 'deg',
        precision = 0.01,
        fmtstr = '%.2f',
    ),
)
