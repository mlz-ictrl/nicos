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
    ]

_selector = make_blocks('Selector', 'selector', [
    BlockRow(Field(name='Preset', dev='selector', istext=True, width=10)),
    BlockRow(Field(name='Lambda', dev='selector_lambda'),
             Field(name='Speed', dev='selector_speed')),
])

_chopper = make_blocks('Chopper', 'chopper', [
    BlockRow(Field(name='Preset', dev='chopper', istext=True, width=17)),
    BlockRow(Field(name='Frequency', dev='chopper_params[0]', unit='Hz'),
             Field(name='Opening', dev='chopper_params[1]', unit='deg')),
])

_collimation = make_blocks('Collimation', 'collimation', [
    BlockRow(Field(name='Preset', dev='collimation', istext=True, width=17)),
])

_detector = make_blocks('Detector', 'detector', [
    BlockRow(Field(name='Preset', dev='detector', istext=True, width=17),
             Field(name='GE HV', dev='gedet_HV', istext=True)),
    BlockRow(
        Field(devices=['det_z', 'beamstop_x', 'beamstop_y'],
              beamstop=True,
              widget='nicos_mlz.kws1.gui.monitorwidgets.Tube', width=70, height=13)
    ),
])

_polarizer = make_blocks('Polarizer', 'polarizer', [
    BlockRow(Field(name='Pol. setting', dev='polarizer', istext=True),
             Field(name='Flipper', dev='flipper', istext=True)),
])

_shutter = make_blocks('Shutter / Outside', 'shutter', [
    BlockRow(Field(name='Shutter', dev='shutter', istext=True, width=9),
             Field(name='NL-3b', dev='nl3b_shutter', istext=True, width=9),
             Field(name='Sixfold', dev='sixfold_shutter', istext=True, width=9)),
])

_sample = make_blocks('Sample', 'sample', [
    BlockRow(Field(name='Trans X', dev='sam_trans_x'),
             Field(name='Trans Y', dev='sam_trans_y'),
             Field(device='ap_sam', widget='nicos_mlz.kws1.gui.monitorwidgets.SampleSlit',
                   width=10, height=10)),
])

_daq = make_blocks('Data acquisition', 'daq', [
    BlockRow(Field(name='Timer', dev='timer'),
             Field(name='Total', dev='det_img[0]', format='%d'),
             Field(name='Rate', dev='det_img[1]', format='%.1f')),
])

_layout = [
    Row(Column(_experiment)),
    Row(Column(*(_selector + _chopper + _polarizer + _daq)),
        Column(*(_shutter + _collimation + _detector + _sample))),
]


devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'KWS-1 status',
        loglevel = 'info',
        cache = 'localhost',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Mono',
        fontsize = 14,
        padding = 3,
        layout = _layout,
    ),
)
