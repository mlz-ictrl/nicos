#  -*- coding: utf-8 -*-

description = 'Virtual setup for the choppers'
group = 'lowlevel'

presets = configdata('config_chopper.CHOPPER_PRESETS')

devices = dict(
    chopper         = device('kws1.switcher.TofSwitcher',
                             description = 'high-level chopper/TOF presets',
                             blockingmove = False,
                             selector = 'selector',
                             det_pos = 'detector',
                             moveables = ['chopper_params', 'det_tof_params'],
                             mappings = dict(
                                 (name, dict((k, [(v['phase'], v['freq']),
                                                  ('tof', v['channels'],
                                                   v['interval'])])
                                             for (k, v) in items.items()))
                                 for (name, items) in presets.items()),
                             fallback = 'unknown',
                             precision = None,
                            ),

    det_tof_params  = device('kws1.switcher.DetTofParams',
                             description = 'parameter setter for TOF params',
                             detector = 'det',
                             lowlevel = True,
                            ),

    chopper1_phase  = device('devices.generic.VirtualMotor',
                             description = 'Phase of the first chopper',
                             unit = 'deg',
                             fmtstr = '%.1f',
                             abslimits = (0, 360),
                             precision = 1.0,
                             lowlevel = True,
                            ),
    chopper1_freq   = device('devices.generic.VirtualMotor',
                             description = 'Frequency of the first chopper',
                             unit = 'Hz',
                             fmtstr = '%.1f',
                             abslimits = (0, 75),
                             precision = 0.1,
                             lowlevel = True,
                            ),
    chopper2_phase  = device('devices.generic.VirtualMotor',
                             description = 'Phase of the second chopper',
                             unit = 'deg',
                             fmtstr = '%.1f',
                             abslimits = (0, 360),
                             precision = 1.0,
                             lowlevel = True,
                            ),
    chopper2_freq   = device('devices.generic.VirtualMotor',
                             description = 'Frequency of the second chopper',
                             unit = 'Hz',
                             fmtstr = '%.1f',
                             abslimits = (0, 75),
                             precision = 0.1,
                             lowlevel = True,
                            ),
    chopper1_motor  = device('devices.generic.VirtualMotor',
                             description = 'Motor switch of the first chopper',
                             lowlevel = True,
                             abslimits = (0, 1),
                             unit = '',
                            ),
    chopper2_motor  = device('devices.generic.VirtualMotor',
                             description = 'Motor switch of the second chopper',
                             lowlevel = True,
                             abslimits = (0, 1),
                             unit = '',
                            ),

    chopper_params  = device('kws1.chopper.Chopper',
                             description = 'Chopper frequency and phase',
                             motor1 = 'chopper1_motor',
                             motor2 = 'chopper2_motor',
                             freq1 = 'chopper1_freq',
                             freq2 = 'chopper2_freq',
                             phase1 = 'chopper1_phase',
                             phase2 = 'chopper2_phase',
                            ),
)

extended = dict(
    poller_cache_reader = ['detector', 'selector', 'det'],
)
