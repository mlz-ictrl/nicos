description = 'setup for the HTML status monitor'
group = 'special'

_experimentcol = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Remark', key='exp/remark', width=80, istext=True, maxlen=80),
        ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        description = 'Status Display',
        title = 'REFSANS Status Monitor',
        filename = '/control/webroot/index.html',
        loglevel = 'info',
        interval = 10,
        cache = 'refsansctrl.refsans.frm2',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 15,
        padding = 5,
        layout = [[_experimentcol],
                  ],
        noexpired = True,
    ),
)
