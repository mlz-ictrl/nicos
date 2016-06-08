#  -*- coding: utf-8 -*-

description = 'setup for the choppers'
group = 'lowlevel'

excludes = ['virtual_chopper']

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'

devices = dict(
    chopper         = device('kws1.chopper.Chopper',
                             description = 'high-level chopper/TOF presets',
                             resolutions = [1, 2.5, 5],
                             selector = 'selector',
                             det_pos = 'detector',
                             params = 'chopper_params',
                             daq = 'det',
                            ),

    chopper_params  = device('kws1.chopper.ChopperParams',
                             description = 'Chopper frequency and opening',
                             motor1 = 'chopper1_motor',
                             motor2 = 'chopper2_motor',
                             freq1 = 'chopper1_freq',
                             freq2 = 'chopper2_freq',
                             phase1 = 'chopper1_phase',
                             phase2 = 'chopper2_phase',
                            ),

    chopper1_phase  = device('devices.tango.WindowTimeoutAO',
                             description = 'Phase of the first chopper',
                             tangodevice = tango_base + 'chopper/phase1',
                             unit = 'deg',
                             fmtstr = '%.1f',
                             precision = 1.0,
                             window = 20.0,
                             timeout = 300.0,
                             lowlevel = True,
                            ),
    chopper1_freq   = device('devices.tango.WindowTimeoutAO',
                             description = 'Frequency of the first chopper',
                             tangodevice = tango_base + 'chopper/freq1',
                             unit = 'Hz',
                             fmtstr = '%.1f',
                             precision = 0.1,
                             window = 20.0,
                             timeout = 300.0,
                             lowlevel = True,
                            ),
    chopper2_phase  = device('devices.tango.WindowTimeoutAO',
                             description = 'Phase of the second chopper',
                             tangodevice = tango_base + 'chopper/phase2',
                             unit = 'deg',
                             fmtstr = '%.1f',
                             precision = 1.0,
                             window = 20.0,
                             timeout = 300.0,
                             lowlevel = True,
                            ),
    chopper2_freq   = device('devices.tango.WindowTimeoutAO',
                             description = 'Frequency of the second chopper',
                             tangodevice = tango_base + 'chopper/freq2',
                             unit = 'Hz',
                             fmtstr = '%.1f',
                             precision = 0.1,
                             window = 20.0,
                             timeout = 300.0,
                             lowlevel = True,
                            ),
    chopper1_motor  = device('devices.tango.DigitalOutput',
                             description = 'Motor switch of the first chopper',
                             tangodevice = tango_base + 'chopper/motor1',
                             lowlevel = True,
                            ),
    chopper2_motor  = device('devices.tango.DigitalOutput',
                             description = 'Motor switch of the second chopper',
                             tangodevice = tango_base + 'chopper/motor2',
                             lowlevel = True,
                            ),
)

extended = dict(
    poller_cache_reader = ['detector', 'selector', 'det'],
)
