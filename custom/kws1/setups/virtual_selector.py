#  -*- coding: utf-8 -*-

description = 'Virtual velocity selector'
group = 'lowlevel'

SELECTOR_PRESETS = {
    '5A':  dict(lam=5,  speed=26730.0),
    '6A':  dict(lam=6,  speed=22275.0),
    '7A':  dict(lam=7,  speed=19092.6),
    '8A':  dict(lam=8,  speed=16706.4),
    '10A': dict(lam=10, speed=13365.0),
    '12A': dict(lam=12, speed=11137.2),
}

devices = dict(
    selector        = device('devices.generic.MultiSwitcher',
                             description = 'select selector presets',
                             moveables = ['selector_speed'],
                             mapping = dict((k, [v['speed']])
                                            for (k, v) in SELECTOR_PRESETS.items()),
                             precision = None,
                            ),

    selector_speed  = device('devices.generic.VirtualMotor',
                             description = 'Selector speed control',
                             unit = 'rpm',
                             fmtstr = '%.0f',
                             warnlimits = (11000, 27000),
                             abslimits = (11000, 27000),
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
