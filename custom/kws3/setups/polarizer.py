# -*- coding: utf-8 -*-

description = 'Polarizer motor setup'
group = 'lowlevel'
display_order = 25

excludes = ['virtual_polarizer']

pol_presets = configdata('config_polarizer.POLARIZER_PRESETS')

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'

devices = dict(
    polarizer = device('devices.generic.MultiSwitcher',
                       description = 'select polarizer presets',
                       blockingmove = False,
                       moveables = ['pol_y', 'pol_tilt'],
                       mapping = {k: [v['y'], v['tilt']]
                                  for (k, v) in pol_presets.items()},
                       fallback = 'unknown',
                       precision = [0.01, 0.01],
                      ),

    pol_y     = device('devices.tango.Motor',
                       description = 'polarizer y-table',
                       tangodevice = tango_base + 'fzjs7/pol_y',
                       unit = 'mm',
                       precision = 0.01,
                      ),
    pol_tilt  = device('devices.tango.Motor',
                       description = 'polarizer tilt',
                       tangodevice = tango_base + 'fzjs7/pol_tilt',
                       unit = 'deg',
                       precision = 0.01,
                      ),
)
