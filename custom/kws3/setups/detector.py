# -*- coding: utf-8 -*-

description = 'Detector motor setup'
group = 'lowlevel'
display_order = 65

excludes = ['virtual_detector']

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'

devices = dict(
    beamstop       = device('kws3.resolution.Beamstop',
                            description = 'select beamstop presets',
                            moveable = 'det_beamstop_x',
                            resolution = 'resolution',
                            outpos = 100,
                           ),

    det_x          = device('devices.tango.Motor',
                            description = 'detector translation X',
                            tangodevice = tango_base + 'fzjs7/det_x',
                            unit = 'mm',
                            precision = 0.01,
                           ),
    det_y          = device('devices.tango.Motor',
                            description = 'detector translation Y',
                            tangodevice = tango_base + 'fzjs7/det_y',
                            unit = 'cm',
                            precision = 0.01,
                           ),
    det_z          = device('devices.tango.Motor',
                            description = 'detector translation Z',
                            tangodevice = tango_base + 'fzjs7/det_z',
                            unit = 'mm',
                            precision = 0.01,
                           ),
    det_beamstop_x = device('devices.tango.Motor',
                            description = 'beamstop x',
                            tangodevice = tango_base + 'fzjs7/beamstop_x',
                            unit = 'mm',
                            precision = 0.1,
                           ),
)

extended = dict(
    poller_cache_reader = ['resolution']
)
