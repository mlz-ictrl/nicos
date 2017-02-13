description = 'setup for the status monitor, HTML version'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title', key='exp/title', width=20, istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=30, istext=True),
                 Field(name='Last file', key='exp/lastscan'),
                ),
        ],
    ),
)


_rightcolumn = Column()

_leftcolumn = Column()

devices = dict(
    Monitor = device('services.monitor.html.Monitor',
                     title = 'NICOS status monitor',
                     filename = '/data/status.html',
                     loglevel = 'info',
                     interval = 3,
                     cache = 'resedahw2.reseda.frm2:14869',
                     prefix = 'nicos/',
                     font = 'Helvetica',
                     valuefont = 'Consolas',
                     fontsize = 17,
                     layout = [[_expcolumn], [_rightcolumn, _leftcolumn]],
                    ),
)
