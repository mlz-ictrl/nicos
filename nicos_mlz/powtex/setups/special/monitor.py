description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title', key='exp/title', width=20,
                       istext=True, maxlen=20),
                 Field(name='Sample', key='sample/samplename', istext=True),
                 Field(name='Remark', key='exp/remark', istext=True),
                 Field(name='Current status', key='exp/action', width=40,
                       istext=True, maxlen=40),
                 Field(name='Last file', key='exp/lastpoint',
                       width=20),
                 )
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'NICOS status monitor',
        loglevel = 'info',
        cache = 'localhost:14869',
        font = 'Open Sans',
        valuefont = 'Mononoki',
        fontsize = 19,
        padding = 0,
        layout = [Row(_expcolumn)],
    ),
)
