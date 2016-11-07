# -*- coding: utf-8 -*-

description = "Virtual detector setup"
group = "lowlevel"
display_order = 20

presets = configdata('config_detector.DETECTOR_PRESETS')
offsets = configdata('config_detector.DETECTOR_OFFSETS')

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

    beamstop_x = device("devices.generic.VirtualMotor",
                        description = "beamstop translation X",
                        unit = "mm",
                        abslimits = (0, 1000),
                        precision = 0.01,
                        speed = 2,
                       ),
    beamstop_y = device("devices.generic.VirtualMotor",
                        description = "beamstop translation Y",
                        unit = "mm",
                        abslimits = (-25, 25),
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
