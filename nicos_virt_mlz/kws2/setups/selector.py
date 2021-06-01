#  -*- coding: utf-8 -*-

description = 'velocity selector'
group = 'lowlevel'
display_order = 15

presets = configdata('config_selector.SELECTOR_PRESETS')

devices = dict(
    selector = device('nicos_mlz.kws2.devices.selector.SelectorSwitcher',
        description = 'select selector presets',
        blockingmove = False,
        moveables = ['selector_speed', 'selector_tilted'],
        det_pos = 'detector',
        presets = presets,
        mapping = {k: [v['speed'], v['tilted']] for (k, v) in presets.items()},
        fallback = 'unknown',
        precision = [10.0, None],
    ),
    selector_speed = device('nicos.devices.generic.VirtualMotor',
        description = 'Selector speed control',
        unit = 'rpm',
        abslimits = (0, 27000),
        curvalue = 25428,
        speed = 1000,
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
    representative = 'selector',
)
