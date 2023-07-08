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

Elemente1 = [
    'chamber_CB',
    'chamber_SFK',
    'chamber_SR',
]

wi=100
he=50
Time_selection1 = [1] + ['day', 24*60*60]

_plot_Block = Block('History motor %d%s' % (Time_selection1[0], Time_selection1[1]) , [
        BlockRow(
            Field(dev=Elemente1[0], plot=Elemente1[0],
                  plotwindow=Time_selection1[0]*Time_selection1[2],
                  width=wi, height=he),
            ),
        BlockRow(
            Field(dev=Elemente1[1], plot=Elemente1[1],
                  plotwindow=Time_selection1[0]*Time_selection1[2],
                  width=wi, height=he),
            ),
        BlockRow(
            Field(dev=Elemente1[2], plot=Elemente1[2],
                  plotwindow=Time_selection1[0]*Time_selection1[2],
                  width=wi, height=he),
            ),
        ],
    )

_plot_col = Column(_plot_Block)

_pumpstandcol = Column(
    Block('pumpstand chamber 2', [
        BlockRow(
            Field(name='CB', dev='chamber_CB'),
            Field(name='SFK', dev='chamber_SFK'),
            Field(name='SR', dev='chamber_SR'),
        ),
    ],),
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
