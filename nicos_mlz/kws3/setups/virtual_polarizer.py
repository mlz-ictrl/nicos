# -*- coding: utf-8 -*-

description = 'Virtual polarizer motor setup'
group = 'lowlevel'
display_order = 25

pol_presets = configdata('config_polarizer.POLARIZER_PRESETS')

devices = dict(
    polarizer = device('nicos.devices.generic.MultiSwitcher',
                       description = 'select polarizer presets',
                       blockingmove = False,
                       moveables = ['pol_y', 'pol_tilt'],
                       mapping = {k: [v['y'], v['tilt']]
                                  for (k, v) in pol_presets.items()},
                       fallback = 'unknown',
                       precision = [0.01, 0.01],
                      ),

    pol_y    = device('nicos_mlz.kws1.devices.virtual.Standin',
                      description = 'polarizer y-table',
                     ),
    pol_tilt = device('nicos_mlz.kws1.devices.virtual.Standin',
                      description = 'polarizer tilt',
                     ),
)
