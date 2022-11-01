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

_andesblock = Block('Instrument', [
    BlockRow(
        Field(widget='nicos_lahn.andes.gui.ANDES',
              width=40, height=30,
              mthdev='omgm',
              mttdev='mtt',
              sthdev='phi',
              sttdev='stt',
              Lmsdev='Lms',
              LtoDdev='Lsd',),
    ),
    ],
)

_shutterblock = Block('Shutters', [
        BlockRow(
            Field(dev='shutter_1'),
            Field(dev='shutter_2'),
            Field(dev='shutter_3'),
        ),
        ],
        setup = 'shutters',
)

_slitblock = Block('Horizontal Beam Delimiter', [
        BlockRow(
            Field(dev='sw'),
        ),
        ],
        setup = 'horizontal_beam_delimiter',
)

_collimatorblock = Block('Collimator', [
        BlockRow(
            Field(dev='hole'),
        ),
        ],
        setup = 'collimator',
)

_monochromatorblock = Block('Monochromator', [
        BlockRow(
            Field(dev='crystal'),
            Field(dev='mtt'),
        ),
        ],
        setup = 'monochromator*',
)

_exchangeblock = Block('Monochromator Exchange', [
        BlockRow(
              Field(dev='tran'),
              Field(dev='inc'),
              Field(dev='cur'),
	      Field(dev='omgm'),
        ),
        ],
        setups = 'monochromator_exchange',
)

_armsblock = Block('Connecting Arms', [
        BlockRow(
              Field(dev='lms'),
              Field(dev='lsd'),
              Field(dev='stt'),
        ),
        ],
        setups = 'connecting_arms*',
)

_sampletableblock = Block('Sample Table', [
        BlockRow(
            Field(dev='x'),
            Field(dev='y'),
            Field(dev='z'),
            Field(dev='phi'),
            Field(dev='chi'),
        ),
        ],
        setups = 'sampletable or goniometer',
)

_leftcolumn = Column(
        _shutterblock, 
        _andesblock,
)

_middlecolumn = Column(
        _monochromatorblock,
        _exchangeblock,
        _sampletableblock,
)

_rightcolumn = Column(
        _slitblock,
        _collimatorblock,
        _armsblock,
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'ANDES status monitor',
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
        ]
    ),
)
