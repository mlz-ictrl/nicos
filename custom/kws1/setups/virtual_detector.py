# -*- coding: utf-8 -*-

description = "Virtual detector setup"
group = "lowlevel"
display_order = 20

presets = configdata('config_detector.DETECTOR_PRESETS')
offsets = configdata('config_detector.DETECTOR_OFFSETS')

devices = dict(
    detector   = device('nicos_mlz.kws1.devices.detector.DetectorPosSwitcher',
                        description = 'high-level detector presets',
                        blockingmove = False,
                        moveables = ['det_z', 'det_x', 'det_y'],
                        presets = presets,
                        offsets = offsets,
                        fallback = 'unknown',
                        precision = [0.01, 0.1, 0.1],
                       ),

    det_x      = device("nicos_mlz.kws1.devices.virtual.Standin",
                        description = "detector translation X",
                       ),
    det_y      = device("nicos_mlz.kws1.devices.virtual.Standin",
                        description = "detector translation Y",
                       ),
    det_z      = device("nicos_mlz.kws1.devices.virtual.Standin",
                        description = "detector translation Z",
                       ),
)
