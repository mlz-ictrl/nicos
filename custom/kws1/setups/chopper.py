#  -*- coding: utf-8 -*-

description = 'setup for the choppers'
group = 'lowlevel'

excludes = ['virtual_chopper']

presets = configdata('config_chopper.CHOPPER_PRESETS')

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'

devices = dict(
    chopper         = device('kws1.switcher.TofSwitcher',
                             description = 'high-level chopper/TOF presets',
                             selector = 'selector',
                             det_pos = 'detector',
                             moveables = ['chopper_params'],
                             mappings = presets,
                             precision = None,
                            ),

    chopper1_phase  = device('devices.tango.WindowTimeoutAO',
                             description = 'Phase of the first chopper',
                             tangodevice = tango_base + 'chopper/phase1',
                             unit = 'deg',
                             fmtstr = '%.1f',
                             precision = 1.0,
                             lowlevel = True,
                            ),
    chopper1_freq   = device('devices.tango.WindowTimeoutAO',
                             description = 'Frequency of the first chopper',
                             tangodevice = tango_base + 'chopper/freq1',
                             unit = 'Hz',
                             fmtstr = '%.1f',
                             precision = 0.1,
                             lowlevel = True,
                            ),
    chopper2_phase  = device('devices.tango.WindowTimeoutAO',
                             description = 'Phase of the second chopper',
                             tangodevice = tango_base + 'chopper/phase2',
                             unit = 'deg',
                             fmtstr = '%.1f',
                             precision = 1.0,
                             lowlevel = True,
                            ),
    chopper2_freq   = device('devices.tango.WindowTimeoutAO',
                             description = 'Frequency of the second chopper',
                             tangodevice = tango_base + 'chopper/freq2',
                             unit = 'Hz',
                             fmtstr = '%.1f',
                             precision = 0.1,
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
