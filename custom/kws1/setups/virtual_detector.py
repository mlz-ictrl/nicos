# -*- coding: utf-8 -*-

description = "Virtual detector setup"
group = "lowlevel"

presets = configdata('config_detector.DETECTOR_PRESETS')

devices = dict(
    detector   = device('kws1.switcher.DetectorPosSwitcher',
                        description = 'high-level detector presets',
                        blockingmove = False,
                        selector = 'selector',
                        moveables = ['det_z', 'det_x', 'det_y'],
                        presets = presets,
                        mappings = dict(
                            (name, dict((k, [v['z'], v['x'], v['y']])
                                        for (k, v) in items.items()))
                            for (name, items) in presets.items()),
                        fallback = 'unknown',
                        precision = [0.01, 0.1, 0.1],
                       ),

    det_x      = device("devices.generic.VirtualMotor",
                        description = "detector translation X",
                        unit = "mm",
                        abslimits = (-50, 50),
                        precision = 0.01,
                        speed = 2,
                       ),
    det_y      = device("devices.generic.VirtualMotor",
                        description = "detector translation Y",
                        unit = "mm",
                        abslimits = (-50, 50),
                        precision = 0.01,
                        speed = 2,
                       ),
    det_z      = device("devices.generic.VirtualMotor",
                        description = "detector translation Z",
                        unit = "m",
                        abslimits = (0, 20),
                        precision = 0.01,
                        speed = 1,
                       ),
)

extended = dict(
    poller_cache_reader = ['selector'],
)
