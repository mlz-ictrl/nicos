description = 'Wave length spread devices'

group = 'lowlevel'

includes = ['alias_lambda']

devices = dict(
    selector_delta_lambda = device('nicos.devices.vendor.astrium.SelectorLambdaSpread',
        description = 'Selector wavelength spread',
        lamdev = 'wl',
        unit = '%',
        fmtstr = '%.1f',
        n_lamellae = 64,
        d_lamellae = 0.4,
        diameter = 0.32,
    ),
)
