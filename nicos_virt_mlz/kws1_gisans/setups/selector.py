description = 'velocity selector'
group = 'lowlevel'
display_order = 15

presets = configdata('config_selector.SELECTOR_PRESETS')

devices = dict(
    selector = device('nicos_mlz.kws1.devices.selector.SelectorSwitcher',
        description = 'select selector presets',
        blockingmove = False,
        moveables = ['selector_speed'],
        det_pos = 'detector',
        presets = presets,
        mapping = {k: [v['speed']] for (k, v) in presets.items()},
        fallback = 'unknown',
        precision = [10.0],
    ),
    selector_speed = device('nicos.devices.generic.VirtualMotor',
        description = 'Selector speed control',
        unit = 'rpm',
        abslimits = (0, 27000),
        curvalue = 25428,
        speed = 1000,
    ),
    selector_lambda = device('nicos_mlz.kws1.devices.selector.SelectorLambda',
        description = 'Selector wavelength control',
        seldev = 'selector_speed',
        unit = 'A',
        fmtstr = '%.2f',
        constant = 2196.7,
    ),
)

extended = dict(
    poller_cache_reader = ['detector'],
    representative = 'selector',
)
