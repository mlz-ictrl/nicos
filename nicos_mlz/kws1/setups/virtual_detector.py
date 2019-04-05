# -*- coding: utf-8 -*-

description = 'Virtual detector setup'
group = 'lowlevel'
display_order = 20

includes = ['virtual_gedet']

presets = configdata('config_detector.DETECTOR_PRESETS')
offsets = configdata('config_detector.DETECTOR_OFFSETS')

devices = dict(
    detector = device('nicos_mlz.kws1.devices.detector.DetectorPosSwitcher',
        description = 'high-level detector presets',
        det_z = 'det_z',
        bs_x = 'beamstop_x',
        bs_y = 'beamstop_y',
        presets = presets,
        offsets = offsets,
        fallback = 'unknown',
    ),
    beamstop_x = device('nicos_mlz.kws1.devices.virtual.Standin',
        description = 'detector translation X',
    ),
    beamstop_y = device('nicos_mlz.kws1.devices.virtual.Standin',
        description = 'detector translation Y',
    ),
    det_z = device('nicos_mlz.kws1.devices.detector.DetectorZAxis',
        description = 'detector translation Z',
        motor = 'det_z_mot',
        hv = 'gedet_HV',
        abslimits = (0.0, 20.01),
    ),
    det_z_mot = device('nicos_mlz.kws1.devices.virtual.Standin',
        description = 'detector translation Z',
        lowlevel = True,
    ),
)

extended = dict(
    representative = 'detector',
)
