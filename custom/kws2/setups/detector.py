# -*- coding: utf-8 -*-

description = "Detector setup"
group = "lowlevel"
display_order = 20

excludes = ['virtual_detector']

presets = configdata('config_detector.DETECTOR_PRESETS')
offsets = configdata('config_detector.DETECTOR_OFFSETS')

tango_base = "tango://phys.kws2.frm2:10000/kws2/"

devices = dict(
    # TODO: small detector
    detector   = device('kws1.detector.DetectorPosSwitcher',
                        description = 'high-level detector presets',
                        blockingmove = False,
                        moveables = ['det_z', 'beamstop_x', 'beamstop_y'],
                        presets = presets,
                        offsets = offsets,
                        fallback = 'unknown',
                        precision = [0.01, 0.1, 0.1],
                       ),

    beamstop_x = device("devices.tango.Motor",
                        description = "detector translation X",
                        tangodevice = tango_base + "fzjs7/beamstop_x",
                        unit = "mm",
                        precision = 0.01,
                       ),
    beamstop_y = device("devices.tango.Motor",
                        description = "detector translation Y",
                        tangodevice = tango_base + "fzjs7/beamstop_y",
                        unit = "mm",
                        precision = 0.01,
                       ),
    det_z      = device("devices.tango.Motor",
                        description = "detector translation Z",
                        tangodevice = tango_base + "fzjs7/detector_z",
                        unit = "m",
                        precision = 0.01,
                       ),
)
