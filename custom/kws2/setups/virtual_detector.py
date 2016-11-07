# -*- coding: utf-8 -*-

description = "Virtual detector setup"
group = "lowlevel"
display_order = 20

includes = ['virtual_gedet']

presets = configdata('config_detector.DETECTOR_PRESETS')
offsets = configdata('config_detector.DETECTOR_OFFSETS')

devices = dict(
    detector   = device('kws2.detector.DetectorPosSwitcher',
                        description = 'high-level detector presets',
                        det_z = 'det_z',
                        bs_x = 'beamstop_x',
                        bs_y = 'beamstop_y',
                        psd_x = 'psd_x',
                        psd_y = 'psd_y',
                        attenuator = 'attenuator',
                        presets = {lam: {p: dict(x=v['x'], y=v['y'],
                                                 z=v.get('z', 0),
                                                 attenuator=v.get('attenuator', 'out'),
                                                 small=v.get('det') == 'small')
                                         for (p, v) in settings.items()}
                                   for (lam, settings) in presets.items()},
                        offsets = offsets,
                        fallback = 'unknown',
                        psdtoppos = 700.0,
                        detbackpos = 20.0,
                       ),

    attenuator = device('devices.generic.ManualSwitch',
                        description = 'virtual attenuator',
                        states = ['out', 'in'],
                       ),

    beamstop_x = device("devices.generic.VirtualMotor",
                        description = "beamstop translation X",
                        unit = "mm",
                        abslimits = (-25, 25),
                        precision = 0.01,
                        speed = 2,
                       ),
    beamstop_y = device("devices.generic.VirtualMotor",
                        description = "beamstop translation Y",
                        unit = "mm",
                        abslimits = (-1000, 1000),  # XXX
                        precision = 0.01,
                        speed = 5,
                       ),
    det_z      = device("kws2.detector.DetectorZAxis",
                        description = "detector translation Z",
                        motor = "det_z_mot",
                        hv = "gedet_HV",
                        abslimits = (0.0, 20.01),
                       ),
    det_z_mot  = device("devices.generic.VirtualMotor",
                        description = "detector translation Z",
                        unit = "m",
                        abslimits = (0, 20.01),
                        precision = 0.01,
                        speed = 1,
                       ),
    psd_x      = device("devices.generic.VirtualMotor",
                        description = "small detector translation X",
                        unit = "mm",
                        abslimits = (-20, 20),
                        precision = 0.01,
                        speed = 5,
                       ),
    psd_y      = device("devices.generic.VirtualMotor",
                        description = "small detector translation Y",
                        unit = "mm",
                        abslimits = (0, 1000),
                        precision = 0.01,
                        speed = 20,
                       ),
)
