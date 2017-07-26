# -*- coding: utf-8 -*-

description = 'Sample rotation and tilt tables'
group = 'optional'
display_order = 36

excludes = ['virtual_sample']

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    sam_rot       = device('nicos.devices.tango.Motor',
                           description = 'sample rotation',
                           tangodevice = tango_base + 'fzjs7/sample_axis_rot',
                           unit = 'deg',
                           precision = 0.01,
                           fmtstr = '%.2f',
                          ),
    sam_tilt      = device('nicos.devices.tango.Motor',
                           description = 'sample tilt',
                           tangodevice = tango_base + 'fzjs7/sample_axis_tilt',
                           unit = 'deg',
                           precision = 0.01,
                           fmtstr = '%.2f',
                          ),
)
