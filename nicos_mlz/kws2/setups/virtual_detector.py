# -*- coding: utf-8 -*-

description = 'Virtual detector setup'
group = 'lowlevel'
display_order = 20

includes = ['virtual_gedet']

presets = configdata('config_detector.DETECTOR_PRESETS')
offsets = configdata('config_detector.DETECTOR_OFFSETS')
small_pos = configdata('config_detector.SMALL_DET_POSITION')

devices = dict(
    detector = device('nicos_mlz.kws2.devices.detector.DetectorPosSwitcher',
        description = 'high-level detector presets',
        det_z = 'det_z',
        bs_x = 'beamstop_x',
        bs_y = 'beamstop_y',
        psd_x = 'psd_x',
        psd_y = 'psd_y',
        attenuator = 'attenuator',
        presets = {
            lam: {
                p: dict(
                    x = v['x'],
                    y = v['y'],
                    z = v.get('z', small_pos),
                    attenuator = v.get('attenuator', 'out'),
                    small = v.get('det') == 'small'
                )
                for (p, v) in settings.items()
            }
            for (lam, settings) in presets.items()
        },
        offsets = offsets,
        fallback = 'unknown',
        psdtoppos = 0.0,
        detbackpos = 20.0,
    ),
    attenuator = device('nicos.devices.generic.ManualSwitch',
        description = 'beam attenuator (S21)',
        states = ['out', 'in'],
    ),
    beamstop_x = device('nicos_mlz.kws1.devices.virtual.Standin',
        description = 'beamstop translation X',
    ),
    beamstop_y = device('nicos_mlz.kws1.devices.virtual.Standin',
        description = 'beamstop translation Y',
    ),
    det_z = device('nicos_mlz.kws2.devices.detector.DetectorZAxis',
        description = 'detector translation Z',
        motor = 'det_z_mot',
        hv = 'gedet_HV',
        abslimits = (0.0, 20.01),
    ),
    det_z_mot = device('nicos_mlz.kws1.devices.virtual.Standin',
        description = 'detector translation Z',
        lowlevel = True,
    ),
    psd_x = device('nicos_mlz.kws1.devices.virtual.Standin',
        description = 'small detector translation X',
    ),
    psd_y = device('nicos_mlz.kws1.devices.virtual.Standin',
        description = 'small detector translation Y',
    ),
)
