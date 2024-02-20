description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='Title', key='exp/title', width=20, istext=True, maxlen=20),
            Field(name='Current status', key='exp/action', width=40,
                  istext=True, maxlen=40),
            Field(name='Last scan file', key='exp/lastscan'),
        ),
        ],
    ),
)

_axisblock = Block('Axes', [
    BlockRow(
        # Field(gui='nicos/clients/gui/panels/tasaxes.ui'),
        Field(name='sgx', dev='sgx'),
    ),
    ],
)

_detectorblock = Block('Detector', [
    BlockRow(
        Field(name='timer', dev='det_timers1'),
        # Field(name='ctr1',  dev='ctr1'),
        # Field(name='ctr2',  dev='ctr2'),
    ),
    ],
    setups='detector',
)

_rightcolumn = Column(_axisblock)

_leftcolumn = Column(_detectorblock)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'NICOS status monitor',
        loglevel = 'info',
        cache = 'localhost:14869',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        padding = 0,
        colors = 'light',
        layout = [
            Row(_expcolumn),
            Row(
                _leftcolumn,
                _rightcolumn,
            ),
        ],
    ),
)
