description = 'Reseda tunewave table support'
group = 'optional'
display_order = 98
includes = ['selector', 'coils', 'cboxes']

packs = ['0a', '0b', '1']
cbox_components = [
    'fg_freq', 'reg_amp','coil1_c1', 'coil1_c2', 'coil1_c1c2serial',
    'coil1_c3', 'coil1_transformer', 'coil2_c1', 'coil2_c2', 'coil2_c1c2serial',
    'coil2_c3', 'coil2_transformer', 'diplexer', 'power_divider'
]

devices = dict(
    echotime = device('nicos_mlz.reseda.devices.tuning.EchoTime',
        description = 'Echo time and tunewave table device',
        wavelength = 'selector_lambda',
        dependencies = ['gf%i' % i for i in ([1, 2] + list(range(4, 11)))]
        + ['hsf_%s' % entry for entry in packs]
        + ['sf_%s' % entry for entry in packs]
        + ['hrf_0a','hrf_0b', 'hrf_1']
        + ['nse0', 'nse1']
        + ['cbox_%s_%s' % (pack, component)
            for pack in packs
            for component in cbox_components],
        zerofirst = {
            'cbox_0a_fg_amp': 0.001,
            'cbox_0b_fg_amp': 0.001,
        },
        stopfirst = ['cbox_0a_reg_amp', 'cbox_0b_reg_amp', 'cbox_1_reg_amp'],
        unit = 'ns',
        fmtstr = '%g'
    ),
)
