description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='Title',    key='exp/title',    width=20, istext=True,
                  maxlen=20),
            Field(name='Current status', key='exp/action', width=40,
                  istext=True, maxlen=40),
        ),
        # BlockRow(
        #     Field(dev='Bus1', name='Bus')
        # )
    ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'NICOS status monitor',
        loglevel = 'info',
        cache = 'kfes64.troja.mff.cuni.cz:14869',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        padding = 0,
        colors = 'light',
        layout = [
            Row(_expcolumn),
        ],
    ),
)
