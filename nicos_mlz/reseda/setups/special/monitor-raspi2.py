description = 'setup for the left status monitor'
group = 'special'

_guidefields = Column(
    Block('Guide Fields', [
        BlockRow('gf0', 'gf1', 'gf2', 'gf4', 'gf5', 'gf6', 'gf7', 'gf8', 'gf9', 'gf10'),
        ],
        setups = 'guide_fields',
    ),
)

_column1 = Column(
    Block('arm0a', [
        BlockRow(Field(name='SF0a', dev='sf_0a'),
                 Field(name='HSF0a', dev='hsf_0a')),
        BlockRow(Field(name='RF0a', dev='cbox_0a_reg_amp'),
                 Field(name='HRF0a', dev='hrf_0a')),
        BlockRow(Field(name='Freq', dev='cbox_0a_fg_freq')),
       # BlockRow(Field(name='FP', dev='cbox_0a_fwdp'),
       #          Field(name='RP', dev='cbox_0a_rwp')),
        BlockRow(Field(name='C1', dev='cbox_0a_coil1_c1'),
                 Field(name='C2', dev='cbox_0a_coil1_c2'),
                 Field(name='C3', dev='cbox_0a_coil1_c3')),
        BlockRow(Field(name='C1C2', dev='cbox_0a_coil1_c1c2serial'),
                 Field(name='Trafo', dev='cbox_0a_coil1_transformer')),
        BlockRow(Field(name='Diplexer', dev='cbox_0a_diplexer'),
                 Field(name='Highpass', dev='cbox_0a_highpass')),
        BlockRow(Field(name='Power Divider', dev='cbox_0a_power_divider')),
        BlockRow(Field(name='T Coil 1', dev='T_arm0a_coil1'),
                 Field(name='T Coil 2', dev='T_arm0a_coil2')),
        ],
        setups='static_flippers and resonance_flippers and cbox_0a and arm_0a',
    ),
)

_column2 = Column(
    Block('arm0b', [
        BlockRow(Field(name='SF0b', dev='sf_0b'),
                 Field(name='HSF0b', dev='hsf_0b')),
        BlockRow(Field(name='RF0b', dev='cbox_0b_reg_amp'),
                 Field(name='HRF0b', dev='hrf_0b')),
        BlockRow(Field(name='Freq', dev='cbox_0b_fg_freq')),
        BlockRow(Field(name='C1', dev='cbox_0b_coil1_c1'),
                 Field(name='C2', dev='cbox_0b_coil1_c2'),
                 Field(name='C3', dev='cbox_0b_coil1_c3')),
        BlockRow(Field(name='C1C2', dev='cbox_0b_coil1_c1c2serial'),
                 Field(name='Trafo', dev='cbox_0b_coil1_transformer')),
        BlockRow(Field(name='Diplexer', dev='cbox_0b_diplexer'),
                 Field(name='Highpass', dev='cbox_0b_highpass')),
        BlockRow(Field(name='Power Divider', dev='cbox_0b_power_divider')),
        BlockRow(Field(name='T Coil 1', dev='T_arm0b_coil1'),
                 Field(name='T Coil 2', dev='T_arm0b_coil2')),
        ],
        setups='static_flippers and resonance_flippers and cbox_0b and arm_0b',
    ),
)

_column3 = Column(
    Block('arm1', [
        BlockRow(Field(name='SF1', dev='sf_1'),
                 Field(name='HSF1', dev='hsf_1')),
        BlockRow(Field(name='RF1', dev='cbox_1_reg_amp'),
                 Field(name='HRF1', dev='hrf_1')),
        BlockRow(Field(name='Freq', dev='cbox_1_fg_freq')),
        BlockRow(Field(name='C1', dev='cbox_1_coil1_c1'),
                 Field(name='C2', dev='cbox_1_coil1_c2'),
                 Field(name='C3', dev='cbox_1_coil1_c3')),
        BlockRow(Field(name='C1C2', dev='cbox_1_coil1_c1c2serial'),
                 Field(name='Trafo', dev='cbox_1_coil1_transformer')),
        BlockRow(Field(name='Diplexer', dev='cbox_1_diplexer'),
                 Field(name='Highpass', dev='cbox_1_highpass')),
        BlockRow(Field(name='Power Divider', dev='cbox_1_power_divider')),
        BlockRow(Field(name='T Coil 1', dev='T_arm1_coil1'),
                 Field(name='T Coil 2', dev='T_arm1_coil2')),
        BlockRow(Field(name='T Coil 3', dev='T_arm1_coil3'),
                 Field(name='T Coil 4', dev='T_arm1_coil4')),
        ],
        setups='static_flippers and resonance_flippers and cbox_1 and arm_1',
    ),
)

_subcoils = Column(
    Block('Field substraction coils', [
        BlockRow(Field(name='NSE 0', dev='nse0'),
                 Field(name='NSE 1', dev='nse1')),
        ],
        setups='sub_coils',
     ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'RESEDA MIEZE Technical',
        loglevel = 'info',
        cache = 'resedahw2.reseda.frm2',
        prefix = 'nicos/',
        font = 'Droid Sans',
        valuefont = 'Consolas',
        fontsize = '14',
        padding = 5,
        colors = 'dark',
        layout = [[_guidefields], [_column1, _column2, _column3], [_subcoils]]
    ),
)
