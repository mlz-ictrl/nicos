#  -*- coding: utf-8 -*-

description = 'Virtual velocity selector'
group = 'lowlevel'

presets = configdata('config_selector.SELECTOR_PRESETS')

devices = dict(
    selector        = device('devices.generic.MultiSwitcher',
                             description = 'select selector presets',
                             blockingmove = False,
                             moveables = ['selector_speed'],
                             mapping = dict((k, [v['speed']])
                                            for (k, v) in presets.items()),
                             fallback = 'unknown',
                             precision = [10.0],
                            ),

    selector_speed  = device('devices.generic.VirtualMotor',
                             description = 'Selector speed control',
                             unit = 'rpm',
                             fmtstr = '%.0f',
                             warnlimits = (11000, 27300),
                             abslimits = (11000, 27300),
                             precision = 10,
                             speed = 700,
                            ),

    selector_lambda = device('kws1.selector.SelectorLambda',
                             description = 'Selector wavelength control',
                             seldev = 'selector_speed',
                             unit = 'A',
                             fmtstr = '%.2f',
                             constant = 2227.5,
                            ),
)
