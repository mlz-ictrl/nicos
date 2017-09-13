#  -*- coding: utf-8 -*-

description = 'Virtual velocity selector'
group = 'lowlevel'
display_order = 15

presets = configdata('config_selector.SELECTOR_PRESETS')

devices = dict(
    selector        = device('nicos_mlz.kws2.devices.selector.SelectorSwitcher',
                             description = 'select selector presets',
                             blockingmove = False,
                             moveables = ['selector_speed', 'selector_tilted'],
                             det_pos = 'detector',
                             presets = presets,
                             mapping = dict((k, [v['speed'], v['tilted']])
                                            for (k, v) in presets.items()),
                             fallback = 'unknown',
                             precision = [10.0, None],
                            ),

    selector_speed  = device('nicos_mlz.kws1.devices.virtual.Standin',
                             description = 'Selector speed control',
                            ),

    selector_tilted = device('nicos.devices.generic.ManualSwitch',
                             description = 'Whether the selector is tilted',
                             states = [False, True],
                             lowlevel = True,
                            ),

    selector_lambda = device('nicos_mlz.kws2.devices.selector.SelectorLambda',
                             description = 'Selector wavelength control',
                             seldev = 'selector_speed',
                             tiltdev = 'selector_tilted',
                             unit = 'A',
                             fmtstr = '%.2f',
                             # values are for [not tilted, tilted]
                             constants = [2094.3286, 1027.5895],
                             offsets = [0.05828, 0.579],
                            ),
)

extended = dict(
    poller_cache_reader = ['detector'],
)
