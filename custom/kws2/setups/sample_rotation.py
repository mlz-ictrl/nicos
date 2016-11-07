# -*- coding: utf-8 -*-

description = "Sample rotation table"
group = "optional"
display_order = 36

excludes = ['virtual_sample']

tango_base = "tango://phys.kws2.frm2:10000/kws2/"

devices = dict(
    sam_rot       = device("devices.tango.Motor",
                           description = "sample rotation",
                           tangodevice = tango_base + "fzjs7/sample_axis_0",
                           unit = "deg",
                           precision = 0.01,
                           fmtstr = "%.2f",
                          ),
)
