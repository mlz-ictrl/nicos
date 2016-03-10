# -*- coding: utf-8 -*-

description = "Detector setup"
group = "lowlevel"

excludes = ['virtual_detector']

presets = configdata('config_detector.DETECTOR_PRESETS')

tango_base = "tango://phys.kws1.frm2:10000/kws1/"

devices = dict(
    detector   = device('kws1.switcher.DetectorPosSwitcher',
                        description = 'high-level detector presets',
                        blockingmove = False,
                        selector = 'selector',
                        moveables = ['det_z', 'det_x', 'det_y'],
                        mappings = dict(
                            (name, dict((k, [v['z'], v['x'], v['y']])
                                        for (k, v) in items.items()))
                            for (name, items) in presets.items()),
                        precision = [0.01, 0.1, 0.1]
                       ),

    det_x      = device("devices.tango.Motor",
                        description = "detector translation X",
                        tangodevice = tango_base + "fzjs7/detector_x",
                        unit = "mm",
                        precision = 0.01,
                       ),
    det_y      = device("devices.tango.Motor",
                        description = "detector translation Y",
                        tangodevice = tango_base + "fzjs7/detector_y",
                        unit = "mm",
                        precision = 0.01,
                       ),
    det_y2     = device("devices.tango.Motor",
                        description = "detector translation Y",
                        tangodevice = tango_base + "fzjs7/detector_y2",
                        unit = "mm",
                        precision = 0.01,
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
                        precision = 0.01,
                       ),

    varbs_1    = device("devices.tango.Motor",
                        description = "variable beamstop 1",
                        tangodevice = tango_base + "fzjs7/varbs_1",
                        unit = "stp",
                        precision = 0.01,
                       ),
)
