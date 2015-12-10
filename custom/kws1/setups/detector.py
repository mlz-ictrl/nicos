# -*- coding: utf-8 -*-

description = "Detector setup"
group = "lowlevel"

tango_base = "tango://phys.kws1.frm2:10000/kws1/"

devices = dict(
    det_x      = device("devices.tango.Motor",
                        description = "detector translation X",
                        tangodevice = tango_base + "fzjs7/detector_x",
                        unit = "mm",
                        precision = 0.001,
                       ),
    det_y      = device("devices.tango.Motor",
                        description = "detector translation Y",
                        tangodevice = tango_base + "fzjs7/detector_y",
                        unit = "mm",
                        precision = 0.001,
                       ),
    det_y2     = device("devices.tango.Motor",
                        description = "detector translation Y",
                        tangodevice = tango_base + "fzjs7/detector_y2",
                        unit = "mm",
                        precision = 0.001,
                        lowlevel = True
                       ),
    det_ydelta = device("kws1.axis.DeltaAxis",
                        description = "difference of detector Y and Y2",
                        axis1 = "det_y",
                        axis2 = "det_y2",
                       ),
    det_z      = device("devices.tango.Motor",
                        description = "detector translation Z",
                        tangodevice = tango_base + "fzjs7/detector_z",
                        unit = "m",
                        precision = 0.001,
                       ),

    varbs_1    = device("devices.tango.Motor",
                        description = "variable beamstop 1",
                        tangodevice = tango_base + "fzjs7/varbs_1",
                        unit = "stp",
                        precision = 0.001,
                       ),
)
