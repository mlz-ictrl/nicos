description = 'setup for the status monitor'
group = 'special'

_experiment = Block('Experiment', [
    BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
             Field(name='Title',    key='exp/title',    width=20,
                   istext=True, maxlen=20),
             Field(name='Sample',   key='sample/samplename', width=15,
                   istext=True, maxlen=15),
             Field(name='Current status', key='exp/action', width=40,
                   istext=True, maxlen=40),
             Field(name='Last file', key='exp/lastpoint')),
])

def make_blocks(name, setup, rows, setups=None):
    import copy
    if setups:
        postfix = ' and (' + setups + ')'
    else:
        postfix = ''
    return [
        Block(name, rows, setups=setup + postfix),
        Block('VIRTUAL ' + name, copy.deepcopy(rows), setups='virtual_' + setup + postfix),
    ]

_selector = make_blocks('Selector', 'selector', [
    BlockRow(Field(name='Preset', dev='selector', istext=True, width=10)),
    BlockRow(Field(name='Lambda', dev='sel_lambda'),
             Field(name='Speed', dev='sel_speed')),
])

_resolution = make_blocks('Resolution', 'resolution', [
    BlockRow(Field(name='Preset', dev='resolution', istext=True, width=17),
             Field(device='sel_ap2', widget='nicos_mlz.kws1.gui.monitorwidgets.SampleSlit',
                   width=10, height=10)),
])

_detector = make_blocks('Detector', 'detector', [
    BlockRow(Field(name='Beamstop', dev='beamstop', istext=True, width=17)),
    BlockRow(Field(dev='det_x'), Field(dev='det_y'), Field(dev='det_z')),
])

_polarizer = make_blocks('Polarizer', 'polarizer', [
    BlockRow(Field(name='Pol. setting', dev='polarizer', istext=True),
             Field(name='Flipper', dev='flipper', istext=True)),
])

_sample = make_blocks('Sample', 'sample', [
    BlockRow(Field(name='Preset', dev='sample_pos', istext=True, width=17)),
    BlockRow(Field(name='Trans X', dev='sam_x'),
             Field(name='Trans Y', dev='sam_y'),
             Field(device='sam_ap', widget='nicos_mlz.kws1.gui.monitorwidgets.SampleSlit',
                   width=10, height=10, maxh=100, maxw=100)),
])

_daq = make_blocks('Data acquisition', 'daq', [
    BlockRow(Field(name='Timer', dev='timer'),
             Field(name='Total', dev='det_img[0]', format='%d'),
             Field(name='Rate', dev='det_img[1]', format='%.1f')),
    BlockRow(Field(name='Mon1', dev='mon1rate'),
             Field(name='Mon2', dev='mon2rate')),
])

_julabo = Block('Sample T', [
    BlockRow('T')
])

_julaboplot = Block('', [
    BlockRow(Field(plot='T', dev='T', width=30, height=25, plotwindow=2*3600),
             Field(plot='T', key='T/setpoint')),
])

_et = Block('Eurotherm', [
    BlockRow('T_et')
], setups='eurotherm')

_etplot = Block('', [
    BlockRow(Field(plot='ET', dev='T_et', width=30, height=25, plotwindow=2*3600),
             Field(plot='ET', key='T_et/setpoint')),
], setups='eurotherm')

_magnet = Block('Electromagnet', [
    BlockRow(Field(name='Current', dev='I_em1')),
], setups='em1')

_layout = [
    Row(Column(_experiment)),
    Row(Column(*(_selector + _polarizer + _daq)),
        Column(*(_resolution + _detector + _sample)),
        Column(_et, _etplot, _julabo, _julaboplot, _magnet)),
]


devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'KWS-3 status',
        loglevel = 'info',
        cache = 'phys.kws3.frm2',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Mono',
        fontsize = 14,
        padding = 3,
        layout = _layout,
    ),
)
