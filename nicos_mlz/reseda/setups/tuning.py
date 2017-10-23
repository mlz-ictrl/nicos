group = 'optional'
description = 'Reseda tunewave table support'

includes = ['selector', 'coils', 'cboxes']

packs = ['0a', '0b', '1']
cbox_components = [
    'freq', 'amp', 'coil1_c1', 'coil1_c2', 'coil1_c1c2serial',
    'coil1_transformer', 'coil2_c1', 'coil2_c2', 'coil2_c1c2serial',
    'coil2_transformer', 'diplexer', 'power_divider'
]

devices = dict(
    echotime = device('nicos_mlz.reseda.devices.tuning.EchoTime',
        description = 'Echo time and tunewave table device',
        wavelength = 'selector_lambda',
        dependencies = ['gf%i' % i for i in range(5)]
        + ['hsf_%s' % entry for entry in packs]
        + ['sf_%s' % entry for entry in packs]
        + ['hrf0', 'hrf1']
        + ['nse0', 'nse1']
        + ['cbox_%s_%s' % (pack, component)
            for pack in packs
            for component in cbox_components],
        unit = 'ns',
        fmtstr = '%g'
    ),
)
