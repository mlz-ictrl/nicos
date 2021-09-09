description = 'setup for the status monitor in the POLI responsible office'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=40,
                       istext=True, maxlen=40),
                 Field(name='Last file', key='exp/lastscan'),
                ),
        ],
    ),
)

_env = Block('Environment', [
    BlockRow(Field(dev='Shutter'), Field(dev='ReactorPower')),
])

_mono = Block('Monochromator', [
    BlockRow(Field(dev='wavelength')),
    BlockRow(Field(dev='changer_m'), Field(dev='theta_m')),
    BlockRow(Field(dev='chi_m'), Field(dev='x_m')),
])

_mono_cu = Block('Cu mono', [
    BlockRow(Field(dev='cuh'), Field(dev='cuv')),
], setups='mono_cu')

_mono_si = Block('Si mono', [
    BlockRow(Field(dev='sih'), Field(dev='siv')),
], setups='mono_si')

_slits = Block('Sample slits', [
    BlockRow(Field(dev='bm', name='Mono slit (bm)', width=24, istext=True)),
    BlockRow(Field(dev='bp', name='Sample slit (bp)', width=24, istext=True)),
    BlockRow(Field(dev='bd', name='Detector slit (bd)', width=24, istext=True)),
], setups='slits')

_table = Block('Sample table', [
    BlockRow(Field(dev='omega'), Field(dev='gamma')),
    BlockRow(Field(dev='liftingctr')),
    BlockRow(Field(dev='chi1'), Field(dev='chi2')),
    BlockRow(Field(dev='xtrans'), Field(dev='ytrans')),
])

_detector = Block('Detector', [
    BlockRow(Field(dev='timer'), Field(dev='ctr1')),
    BlockRow(Field(dev='mon1'), Field(dev='mon2')),
], setups='detector')

_hecells = Block('He cell', [
    BlockRow(Field(dev='beam_trans'), Field(dev='beam_pol')),
], setups='hecells')

_mezei = Block('Mezei flipper', [
    BlockRow(Field(dev='mezeiflipper')),
    BlockRow(Field(dev='mezeiflipcur'), Field(dev='mezeicompcur')),
], setups='mezei_flipper')

_bender = Block('Bender', [
    BlockRow(Field(dev='bender_rot'), Field(dev='bender_trans')),
], setups='bender')

_cryopad = Block('Cryopad', [
    BlockRow(Field(dev='Pin'), Field(dev='Pout')),
    BlockRow(Field(dev='Fin'), Field(dev='Fout')),
], setups='cryopad')

_cryopad_currents = Block('Currents', [
    BlockRow(Field(dev='nutator1c'), Field(dev='nutator2c'), Field(dev='nutax')),
    BlockRow(Field(dev='pc1'), Field(dev='pc2'), Field(dev='pcflipper')),
    BlockRow(Field(dev='decpolcorr1'), Field(dev='decpolcorr2'), Field(dev='decpolmain')),
    BlockRow(Field(dev='polarcorr1'), Field(dev='polarcorr2'), Field(dev='polarmain')),
], setups='cryopad_currents')

_nutator = Block('Nutator', [
    BlockRow(Field(dev='nutator1'), Field(dev='nutator2')),
], setups='nutator')

_layout = [
    Row(_expcolumn),
    Row(
        Column(_env, _mono, _mono_cu, _mono_si, _hecells, _bender),
        Column(_slits, _table),
        Column(_mezei, _cryopad, _cryopad_currents, _nutator, _detector)
    ),
]

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'NICOS status monitor',
        loglevel = 'info',
        cache = 'phys.poli.frm2',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Mono',
        fontsize = 20,
        padding = 2,
        layout = _layout,
    ),
)
