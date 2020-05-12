description = 'setup for the status monitor, HTML version'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=30,
                       istext=True),
                 Field(name='Last file', key='exp/lastscan'),
                ),
        ],
    ),
)

_axisblock = Block('Axes', [
    BlockRow(
        Field(name='sgx', dev='sgx'),
    ),
    ],
)

_detectorblock = Block('Detector', [
    BlockRow(
        Field(name='timer', dev='det_timers1'),
        # Field(name='ctr1',  dev='ctr1'),
        # Field(name='ctr2',  dev='ctr2')),
    ),
    ],
    setups='detector',
)

_tasblock = Block('Triple-axis', [
    BlockRow(Field(dev='tas[0]', name='H', format='%.3f', unit=''),
             Field(dev='tas[1]', name='K', format='%.3f', unit=''),
             Field(dev='tas[2]', name='L', format='%.3f', unit=''),
             Field(dev='tas[3]', name='E', format='%.3f', unit='')),
    BlockRow(Field(key='tas/scanmode', name='Mode'),
             Field(dev='mono', name='ki'),
             Field(dev='ana', name='kf'),
             Field(key='tas/energytransferunit', name='Unit')),
    ],
    setups='tas',
)

_rightcolumn = Column(_axisblock)

_leftcolumn = Column(_tasblock, _detectorblock)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'NICOS status monitor',
        filename = 'data/status.html',
        loglevel = 'info',
        interval = 3,
        cache = 'localhost:14869',
        prefix = 'nicos/',
        font = 'Helvetica',
        valuefont = 'Consolas',
        fontsize = 17,
        layout = [[_expcolumn],
                  [_rightcolumn, _leftcolumn]],
    ),
)
