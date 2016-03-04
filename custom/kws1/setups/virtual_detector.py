# -*- coding: utf-8 -*-

description = "Virtual detector setup"
group = "lowlevel"

DETECTOR_PRESETS = {
    '4m':  dict(z=4, x=0, y=0),
    '8m':  dict(z=8, x=2, y=10),
    '20m': dict(z=20, x=10, y=10),
}

devices = dict(
    detector   = device('devices.generic.MultiSwitcher',
                        description = 'select detector presets',
                        moveables = ['det_z', 'det_x', 'det_y'],
                        mapping = dict((k, [v['z'], v['x'], v['y']])
                                       for (k, v) in DETECTOR_PRESETS.items()),
                        precision = [0.01, 0.1, 0.1]
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
