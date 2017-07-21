#  -*- coding: utf-8 -*-

description = 'Virtual setup for the choppers'
group = 'lowlevel'
display_order = 65

devices = dict(
    chopper         = device('nicos_mlz.kws1.devices.chopper.Chopper',
                             description = 'high-level chopper/TOF presets',
                             resolutions = [1, 2.5, 5, 10],
                             selector = 'selector',
                             det_pos = 'detector',
                             params = 'chopper_params',
                             daq = 'det',
                            ),

    chopper_params  = device('nicos_mlz.kws1.devices.chopper.ChopperParams',
                             description = 'Chopper frequency and opening',
                             freq1 = 'chopper1_freq',
                             freq2 = 'chopper2_freq',
                             phase1 = 'chopper1_phase',
                             phase2 = 'chopper2_phase',
                             fmtstr = '%.2f Hz, %.0f deg',
                            ),

    chopper1_phase  = device('nicos_mlz.kws1.devices.virtual.Standin',
                             description = 'Phase of the first chopper',
                             fmtstr = '%.2f',
                             lowlevel = True,
                            ),
    chopper1_freq   = device('nicos_mlz.kws1.devices.virtual.Standin',
                             description = 'Frequency of the first chopper',
                             fmtstr = '%.2f',
                             lowlevel = True,
                            ),
    chopper2_phase  = device('nicos_mlz.kws1.devices.virtual.Standin',
                             description = 'Phase of the second chopper',
                             fmtstr = '%.2f',
                             lowlevel = True,
                            ),
    chopper2_freq   = device('nicos_mlz.kws1.devices.virtual.Standin',
                             description = 'Frequency of the second chopper',
                             fmtstr = '%.2f',
                             lowlevel = True,
                            ),
)

extended = dict(
    poller_cache_reader = ['detector', 'selector', 'det'],
)
