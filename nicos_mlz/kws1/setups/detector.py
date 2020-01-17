# -*- coding: utf-8 -*-

description = 'Detector setup'
group = 'lowlevel'
display_order = 20

includes = ['gedet', 'vacuumsys']
excludes = ['virtual_detector']

presets = configdata('config_detector.DETECTOR_PRESETS')
offsets = configdata('config_detector.DETECTOR_OFFSETS')

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'

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
    beamstop_x = device('nicos.devices.tango.Motor',
        description = 'beamstop translation X',
        tangodevice = tango_base + 'fzjs7/beamstop_x',
        unit = 'mm',
        precision = 0.1,
    ),
    beamstop_y = device('nicos.devices.tango.Motor',
        description = 'beamstop translation Y',
        tangodevice = tango_base + 'fzjs7/beamstop_y',
        unit = 'mm',
        precision = 2.0,
    ),
    det_z = device('nicos_mlz.kws1.devices.detector.DetectorZAxis',
        description = 'detector translation Z',
        motor = 'det_z_mot',
        hv = 'gedet_HV',
        abslimits = (1.49, 20.10),
    ),
    det_z_mot = device('nicos_mlz.kws1.devices.detector.LockedMotor',
        description = 'detector translation Z',
        tangodevice = tango_base + 'fzjs7/detector_z',
        unit = 'm',
        precision = 0.002,
        lowlevel = True,
    ),
)

extended = dict(
    representative = 'detector',
)
