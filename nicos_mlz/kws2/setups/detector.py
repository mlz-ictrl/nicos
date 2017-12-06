# -*- coding: utf-8 -*-

description = 'Detector setup'
group = 'lowlevel'
display_order = 20

includes = ['gedet', 'vacuumsys']
excludes = ['virtual_detector']

presets = configdata('config_detector.DETECTOR_PRESETS')
offsets = configdata('config_detector.DETECTOR_OFFSETS')
small_pos = configdata('config_detector.SMALL_DET_POSITION')

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

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
    attenuator = device('nicos_mlz.kws2.devices.attenuator.Attenuator',
        description = 'beam attenuator (S21)',
        input = 'atten_in',
        output = 'atten_set',
        timeout = 300.,
    ),
    atten_in = device('nicos.devices.tango.DigitalInput',
        tangodevice = tango_base + 'fzjdp_digital/s21_read',
        lowlevel = True,
    ),
    atten_set = device('nicos.devices.tango.DigitalOutput',
        tangodevice = tango_base + 'fzjdp_digital/s21_write',
        lowlevel = True,
    ),
    beamstop_x = device('nicos.devices.tango.Motor',
        description = 'beamstop translation X',
        tangodevice = tango_base + 'fzjs7/beamstop_x',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.1f',
    ),
    beamstop_y = device('nicos.devices.tango.Motor',
        description = 'beamstop translation Y',
        tangodevice = tango_base + 'fzjs7/beamstop_y',
        unit = 'mm',
        precision = 1.5,
        fmtstr = '%.1f',
    ),
    beamstop_y_encoder = device('nicos_mlz.kws2.devices.detector.DetectorBsEncoder',
        description = 'additional encoder of beamstop translation Y',
        tangodevice = tango_base + 'fzjdp_analog/beamstop_y_encoder',
        unit = 'mm',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    det_z = device('nicos_mlz.kws2.devices.detector.DetectorZAxis',
        description = 'detector translation Z',
        motor = 'det_z_mot',
        hv = 'gedet_HV',
        abslimits = (0.0, 20.01),
    ),
    det_z_mot = device('nicos_mlz.kws2.devices.detector.LockedMotor',
        description = 'detector translation Z',
        tangodevice = tango_base + 'fzjs7/detector_z',
        unit = 'm',
        precision = 0.002,
        lowlevel = True
    ),
    psd_x = device('nicos_mlz.kws2.devices.detector.LockedMotor',
        description = 'small detector translation X',
        tangodevice = tango_base + 'fzjs7/psd_x',
        unit = 'mm',
        precision = 0.01,
    ),
    psd_y = device('nicos_mlz.kws2.devices.detector.LockedMotor',
        description = 'small detector translation Y',
        tangodevice = tango_base + 'fzjs7/psd_y',
        unit = 'mm',
        precision = 0.01,
    ),
)
