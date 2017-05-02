# -*- coding: utf-8 -*-

description = 'Virtual detector motor setup'
group = 'lowlevel'
display_order = 65

devices = dict(
    beamstop       = device('kws3.resolution.Beamstop',
                            description = 'select beamstop presets',
                            moveable = 'det_beamstop_x',
                            resolution = 'resolution',
                            outpos = 100,
                           ),

    det_x          = device('kws1.virtual.Standin',
                            description = 'detector translation X',
                           ),
    det_y          = device('kws1.virtual.Standin',
                            description = 'detector translation Y',
                           ),
    det_z          = device('kws1.virtual.Standin',
                            description = 'detector translation Z',
                           ),
    det_beamstop_x = device('kws1.virtual.Standin',
                            description = 'detector beamstop_x',
                           ),
)

extended = dict(
    poller_cache_reader = ['resolution']
)
