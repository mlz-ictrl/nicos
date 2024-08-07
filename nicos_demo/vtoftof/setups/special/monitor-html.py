description = 'setup for the status HTML monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='Title',    key='exp/title',    width=20,
                  istext=True, maxlen=20),
            Field(name='Current status', key='exp/action', width=40,
                  istext=True, maxlen=40),
            Field(name='Last file', key='exp/lastscan'),),
        ],
    ),
)

_frm = Column(
    Block('FRM II', [
        BlockRow(Field(dev='ReactorPower',)),
    ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'NICOS status monitor',
        loglevel = 'info',
        interval = 10,
        filename = 'webroot/index.html',
        cache = configdata('config_data.host'),
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        padding = 0,
        fontsize = 24,
        layout = [
            Row(_expcolumn),
            Row(_frm),
        ],
    ),
)
