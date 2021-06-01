# -*- coding: utf-8 -*-

description = 'Virtual detector setup'
group = 'lowlevel'
display_order = 20

includes = ['gedet']

presets = configdata('config_detector.DETECTOR_PRESETS')
offsets = configdata('config_detector.DETECTOR_OFFSETS')
small_pos = configdata('config_detector.SMALL_DET_POSITION')

devices = dict(
    detector = device('nicos_mlz.kws1.devices.detector.DetectorPosSwitcher',
        description = 'high-level detector presets',
        det_z = 'det_z',
        bs_x = 'beamstop_x',
        bs_y = 'beamstop_y',
        presets = presets,
        offsets = offsets,
        fallback = 'unknown',
        beamstopsettlepos = None,
    ),
    beamstop_x = device('nicos.devices.generic.VirtualMotor',
        description = 'detector translation X',
        unit = 'mm',
        abslimits = (-50, 50),
        speed = 4,
        curvalue = 0,
    ),
    beamstop_y = device('nicos.devices.generic.VirtualMotor',
        description = 'detector translation Y',
        unit = 'mm',
        abslimits = (0, 1000),
        speed = 8,
        curvalue = 500,
    ),
    det_z = device('nicos_mlz.kws1.devices.detector.DetectorZAxis',
        description = 'detector translation Z',
        motor = 'det_z_mot',
        hv = 'gedet_HV',
        abslimits = (0.0, 20.01),
    ),
    det_z_mot = device('nicos.devices.generic.VirtualMotor',
        description = 'detector translation Z',
        lowlevel = True,
        unit = 'm',
        abslimits = (0, 20.01),
        speed = 0.5,
        curvalue = 8,
    ),
)

extended = dict(
    representative = 'detector',
)
