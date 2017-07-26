# -*- coding: utf-8 -*-

description = 'Virtual selector area setup'
group = 'lowlevel'
display_order = 20

sel_presets = configdata('config_selector.SELECTOR_PRESETS')

devices = dict(
    selector        = device('nicos.devices.generic.MultiSwitcher',
                             description = 'select selector presets',
                             blockingmove = False,
                             moveables = ['sel_lambda'],
                             mapping = {k: [v['lam']]
                                        for (k, v) in sel_presets.items()},
                             fallback = 'unknown',
                             precision = [0.05],
                            ),

    sel_speed       = device('nicos_mlz.kws1.devices.virtual.Standin',
                             description = 'selector speed',
                            ),

    sel_lambda      = device('nicos_mlz.kws1.devices.selector.SelectorLambda',
                             description = 'Selector wavelength control',
                             seldev = 'sel_speed',
                             unit = 'A',
                             fmtstr = '%.2f',
                             constant = 3133.4 / 60,  # SelectorLambda uses RPM
                             offset = -0.00195,
                            ),

    sel_rot         = device('nicos_mlz.kws1.devices.virtual.Standin',
                             description = 'selector rotation table',
                            ),
)
