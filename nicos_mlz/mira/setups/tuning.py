description = 'MIRA tunewave table support'
group = 'optional'
display_order = 98
includes = ['cbox2', 'cbox1']

packs = ['1', '2']
cbox_components = [
    'fg_freq', 'reg_amp','coil1_c1', 'coil1_c2', 'coil1_c1c2serial',
    'coil1_c3', 'coil1_transformer', 'coil2_c1', 'coil2_c2', 'coil2_c1c2serial',
    'coil2_c3', 'coil2_transformer', 'diplexer', 'power_divider'
]

modules = ['nicos_mlz.reseda.tuning_commands',  'nicos_mlz.mira.commands']


devices = dict(
    echotime = device('nicos_mlz.reseda.devices.tuning.EchoTime',
        description = 'Echo time and tunewave table device',
        wavelength = 'lam',
        dependencies = ['cbox%s_%s' % (pack, component)
            for pack in packs
            for component in cbox_components] +
            ['psd_chop_freq', 'psd_timebin_freq', 'psd_chop_amp', 'psd_timebin_amp'] +
            ['dct5', 'dct6'] +
            ['hrf1', 'hrf2', 'hsf1', 'hsf2', 'sf1', 'sf2'],
        zerofirst = {
            'cbox1_fg_amp': 0.01,
            'cbox2_fg_amp': 0.01,
        },
        stopfirst = ['cbox1_reg_amp', 'cbox2_reg_amp'],
        unit = 'ns',
        fmtstr = '%g'
    ),
)
