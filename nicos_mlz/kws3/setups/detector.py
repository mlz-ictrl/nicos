# -*- coding: utf-8 -*-

description = 'Detector motor setup'
group = 'lowlevel'
display_order = 65

includes = ['beamstop']
excludes = ['virtual_detector']

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'
s7_motor = tango_base + 's7_motor/'

devices = dict(
    det_x = device('nicos.devices.entangle.Motor',
        description = 'detector translation X',
        tangodevice = s7_motor + 'det_x',
        unit = 'mm',
        precision = 0.01,
    ),
    det_y = device('nicos.devices.entangle.Motor',
        description = 'detector translation Y',
        tangodevice = s7_motor + 'det_y',
        unit = 'cm',
        precision = 0.01,
    ),
    det_z = device('nicos.devices.entangle.Motor',
        description = 'detector translation Z',
        tangodevice = s7_motor + 'det_z',
        unit = 'mm',
        precision = 0.01,
    ),
    det_pos = device('nicos_mlz.kws3.devices.combined.Detector',
        description = 'overall detector position',
        x = 'det_x',
        y = 'det_y',
        z = 'det_z',
    ),
)

extended = dict(
    representative = 'det_pos',
)
