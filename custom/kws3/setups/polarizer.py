# -*- coding: utf-8 -*-

description = "Polarizer motor setup"
group = "lowlevel"

excludes = ['virtual_polarizer']

tango_base = "tango://phys.kws3.frm2:10000/kws3/"

devices = dict(

    pol_y    = device("devices.tango.Motor",
                      description = "polarizer y-table",
                      tangodevice = tango_base + "fzjs7/pol_y",
                      unit = "mm",
                      precision = 0.01,
                     ),
    pol_tilt = device("devices.tango.Motor",
                      description = "polarizer tilt",
                      tangodevice = tango_base + "fzjs7/pol_tilt",
                      unit = "deg",
                      precision = 0.01,
                     ),
)
