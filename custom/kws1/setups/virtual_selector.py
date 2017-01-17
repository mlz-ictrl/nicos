#  -*- coding: utf-8 -*-

description = 'Virtual velocity selector'
group = 'lowlevel'
display_order = 15

presets = configdata('config_selector.SELECTOR_PRESETS')

devices = dict(
    selector        = device('kws1.selector.SelectorSwitcher',
                             description = 'select selector presets',
                             blockingmove = False,
                             moveables = ['selector_speed'],
                             det_pos = 'detector',
                             presets = presets,
                             mapping = dict((k, [v['speed']])
                                            for (k, v) in presets.items()),
                             fallback = 'unknown',
                             precision = [10.0],
                            ),

    selector_speed  = device('kws1.virtual.Standin',
                             description = 'Selector speed control',
                            ),

    selector_lambda = device('kws1.selector.SelectorLambda',
                             description = 'Selector wavelength control',
                             seldev = 'selector_speed',
                             unit = 'A',
                             fmtstr = '%.2f',
                             constant = 2227.5,
                            ),
)

extended = dict(
    poller_cache_reader = ['detector'],
)
