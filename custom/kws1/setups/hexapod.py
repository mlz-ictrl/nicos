# -*- coding: utf-8 -*-

description = "Hexapod control"
group = "optional"
display_order = 70

excludes = []

tango_base = "tango://phys.kws1.frm2:10000/kws1/"

devices = dict(
    hexapod_dt    = device("devices.tango.Motor",
                           description = "Hexapod base rotation table",
                           tangodevice = tango_base + "hexapodbase/dt",
                           unit = "deg",
                           precision = 0.01,
                           fmtstr = "%.2f",
                          ),
    hexapod_rx    = device("devices.tango.Motor",
                           description = "Hexapod rotation around X",
                           tangodevice = tango_base + "hexapodbase/rx",
                           unit = "deg",
                           precision = 0.01,
                           fmtstr = "%.2f",
                          ),
    hexapod_ry    = device("devices.tango.Motor",
                           description = "Hexapod rotation around Y",
                           tangodevice = tango_base + "hexapodbase/ry",
                           unit = "deg",
                           precision = 0.01,
                           fmtstr = "%.2f",
                          ),
    hexapod_rz    = device("devices.tango.Motor",
                           description = "Hexapod rotation around Z",
                           tangodevice = tango_base + "hexapodbase/rz",
                           unit = "deg",
                           precision = 0.01,
                           fmtstr = "%.2f",
                          ),
    hexapod_tx    = device("devices.tango.Motor",
                           description = "Hexapod translation in X",
                           tangodevice = tango_base + "hexapodbase/tx",
                           unit = "mm",
                           precision = 0.1,
                           fmtstr = "%.1f",
                          ),
    hexapod_ty    = device("devices.tango.Motor",
                           description = "Hexapod translation in Y",
                           tangodevice = tango_base + "hexapodbase/ty",
                           unit = "mm",
                           precision = 0.1,
                           fmtstr = "%.1f",
                          ),
    hexapod_tz    = device("devices.tango.Motor",
                           description = "Hexapod translation in Z",
                           tangodevice = tango_base + "hexapodbase/tz",
                           unit = "mm",
                           precision = 0.1,
                           fmtstr = "%.1f",
                          ),
)
