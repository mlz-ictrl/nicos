description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='Title', key='exp/title', width=20, istext=True,
                  maxlen=20),
            Field(name='Current status', key='exp/action', width=40,
                  istext=True, maxlen=40),
            Field(name = 'Last file', key = 'exp/lastscan'),
        ),
        ],
    ),
)

_shutterblock = Block('Shutters', [
    BlockRow(
        Field(dev='shutter_1'),
        Field(dev='shutter_2'),
        Field(dev='fastshutter'),
        Field(dev='shutter_3'),
        ),
    ],
    setups='shutters',
)

_collimatorblock = Block('Collimator', [
    BlockRow(
        Field(dev='collimator'),
        Field(dev='pinhole'),
        ),
    ],
    setups='collimator',
)

_sblblock = Block('Small Beam Limiter', [
    BlockRow(
        Field(dev='sbl'),
        ),
    ],
    setups='small_beam_limiter',
)

_filterblock = Block('Filter', [
    BlockRow(
        Field(dev='crystal'),
        ),
    ],
    setups='filter',
)

_lblblock = Block('Large Beam Limiter', [
    BlockRow(
        Field(dev='lbl'),
        ),
    ],
    setups='large_beam_limiter',
)

_huberblock = Block('HUBER Small Sample Manipulator', [
    BlockRow(
        Field(dev='x'),
        Field(dev='y'),
        Field(dev='z'),
        Field(dev='phi'),
    ),
    ],
    setups='sampletable',
)

_detector_translationblock = Block('Detector Translation', [
    BlockRow(
        Field(dev='dtx'),
        Field(dev='dty'),
        ),
    ],
    setups='detector_translation',
)

_selectorblock = Block('Velocity Selector', [
    BlockRow(
        Field(name='Speed', dev='selector'),
    ),
    ],
    setups='selector',
)

_monochromatorblock = Block('Double Crystal Monochromator', [
    BlockRow(
        Field(name='Lambda', dev='mono'),
        Field(name='Position', dev='mono_inout')
    ),
    BlockRow(
        Field(dev='mr1'),
        Field(dev='mr2'),
        Field(dev='mtz'),
    ),
    ],
    setups='monochromator',
)

_ngiblock = Block('Neutron Grating Interferometer', [
    BlockRow(
        Field(dev='tx'),
        Field(dev='ry'),
        Field(dev='rz'),
    ),
    ],
    setups='ngi',
)

_leftcolumn = Column(
    _shutterblock,
    _collimatorblock,
    _filterblock,
)

_middlecolumn = Column(
    _sblblock,
    _lblblock,
    _huberblock,
    _detector_translationblock,
)

_rightcolumn = Column(
    _selectorblock,
    _monochromatorblock,
    _ngiblock,
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'NICOS status monitor',
        loglevel = 'info',
        # Use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the hostname (official
        # computer name) or an IP address.
        cache = 'localhost',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        padding = 0,
        layout = [
            Row(_expcolumn),
            Row(_leftcolumn, _middlecolumn, _rightcolumn),
        ],
    ),
)
