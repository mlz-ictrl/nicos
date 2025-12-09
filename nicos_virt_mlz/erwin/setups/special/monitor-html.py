description = 'setup for the status monitor, HTML version'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=30,
                       istext=True),
                 Field(name='Last scan file', key='exp/lastscan'),
                 Field(name='Last image file', key='exp/lastpoint'),
                ),
        ],
    ),
)

_rightcolumn = Column()

_leftcolumn = Column()

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'NICOS status monitor',
        filename = 'data/status.html',
        loglevel = 'info',
        interval = 3,
        cache = configdata('config_data.cache_host'),
        prefix = 'nicos/',
        font = 'Helvetica',
        valuefont = 'Consolas',
        fontsize = 17,
        layout = [
            Row(_expcolumn),
            Row(_leftcolumn, _rightcolumn),
        ],
    ),
)
