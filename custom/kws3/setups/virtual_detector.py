# -*- coding: utf-8 -*-

description = 'Virtual detector motor setup'
group = 'lowlevel'
display_order = 65

devices = dict(
    beamstop       = device('devices.generic.MultiSwitcher',
                            description = 'select beamstop presets',
                            blockingmove = False,
                            moveables = ['det_beamstop_x'],
                            # TODO: add proper presets
                            mapping = {'out': [112],
                                       'in': [0]},
                            fallback = 'unknown',
                            precision = [0.01],
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
