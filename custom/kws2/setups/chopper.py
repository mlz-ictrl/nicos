#  -*- coding: utf-8 -*-

description = 'setup for the choppers'
group = 'lowlevel'
display_order = 65

excludes = ['virtual_chopper']

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    chopper         = device('kws1.chopper.Chopper',
                             description = 'high-level chopper/TOF presets',
                             resolutions = [2.5, 5, 10],
                             fmtstr = '%.2f Hz, %.0f deg',
                             selector = 'selector',
                             det_pos = 'detector',
                             params = 'chopper_params',
                             daq = 'det',
                             channels = 64,
                            ),

    chopper_params  = device('kws1.chopper.ChopperParams',
                             description = 'Chopper frequency and opening',
                             freq1 = 'chopper1_freq',
                             freq2 = 'chopper2_freq',
                             phase1 = 'chopper1_phase',
                             phase2 = 'chopper2_phase',
                             fmtstr = '%.2f Hz, %.0f deg',
                            ),

    chopper1_phase  = device('devices.tango.WindowTimeoutAO',
                             description = 'Phase of the first chopper',
                             tangodevice = tango_base + 'chopper/phase1',
                             unit = 'deg',
                             fmtstr = '%.2f',
                             precision = 0.5,  # should be < 1.0
                             window = 20.0,
                             timeout = 1800.0,
                             lowlevel = True,
                            ),
    chopper1_freq   = device('kws1.chopper.ChopperFrequency',
                             description = 'Frequency of the first chopper',
                             tangodevice = tango_base + 'chopper/freq1',
                             unit = 'Hz',
                             fmtstr = '%.2f',
                             precision = 0.1,
                             window = 20.0,
                             timeout = 1800.0,
                             lowlevel = True,
                            ),
    chopper2_phase  = device('devices.tango.WindowTimeoutAO',
                             description = 'Phase of the second chopper',
                             tangodevice = tango_base + 'chopper/phase2',
                             unit = 'deg',
                             fmtstr = '%.2f',
                             precision = 0.5,
                             window = 20.0,
                             timeout = 1800.0,
                             lowlevel = True,
                            ),
    chopper2_freq   = device('devices.tango.WindowTimeoutAO',
                             description = 'Frequency of the second chopper',
                             tangodevice = tango_base + 'chopper/freq2',
                             unit = 'Hz',
                             fmtstr = '%.2f',
                             precision = 0.1,
                             window = 20.0,
                             timeout = 1800.0,
                             lowlevel = True,
                            ),
)

extended = dict(
    poller_cache_reader = ['detector', 'selector', 'det'],
)
