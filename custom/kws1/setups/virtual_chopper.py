#  -*- coding: utf-8 -*-

description = 'Virtual setup for the choppers'
group = 'lowlevel'
display_order = 65

devices = dict(
    chopper         = device('kws1.chopper.Chopper',
                             description = 'high-level chopper/TOF presets',
                             resolutions = [1, 2.5, 5, 10],
                             fmtstr = '%.2f Hz, %.0f deg',
                             selector = 'selector',
                             det_pos = 'detector',
                             params = 'chopper_params',
                             daq = 'det',
                            ),

    chopper_params  = device('kws1.chopper.ChopperParams',
                             description = 'Chopper frequency and opening',
                             freq1 = 'chopper1_freq',
                             freq2 = 'chopper2_freq',
                             phase1 = 'chopper1_phase',
                             phase2 = 'chopper2_phase',
                             fmtstr = '%.2f Hz, %.0f deg',
                            ),

    chopper1_phase  = device('kws1.virtual.Standin',
                             description = 'Phase of the first chopper',
                             lowlevel = True,
                            ),
    chopper1_freq   = device('kws1.virtual.Standin',
                             description = 'Frequency of the first chopper',
                             lowlevel = True,
                            ),
    chopper2_phase  = device('kws1.virtual.Standin',
                             description = 'Phase of the second chopper',
                             lowlevel = True,
                            ),
    chopper2_freq   = device('kws1.virtual.Standin',
                             description = 'Frequency of the second chopper',
                             lowlevel = True,
                            ),
)

extended = dict(
    poller_cache_reader = ['detector', 'selector', 'det'],
)
