description = 'colli'
group = 'special'

Time_selection1 = [10,'day',24*60*60]
Time_selection2 = [10,'hour', 10*60]
Time_selection3h = [3,'h',60*60]

Elemente1 = [
    'shutter_gamma_motor',
    'nok2r_motor',
    'nok2s_motor',
    'nok3r_motor',
    'nok3s_motor',
    'nok4r_motor',
    'nok4s_motor',
    'nok6r_motor',
    'nok6s_motor',
    'nok7r_motor',
    'nok7s_motor',
    'nok8r_motor',
    'nok8s_motor',
    'nok9r_motor',
    'nok9s_motor',
    'zb0_motor',
    'zb1_motor',
    'zb2_motor',
    'zb3r_motor',
    'zb3s_motor',
    'bs1s_motor',
    'bs1r_motor',
    ]

Elemente2 = [
    'shutter_gamma_acc',
    'nok2r_acc',
    'nok2s_acc',
    'nok3r_acc',
    'nok3s_acc',
    'nok4r_acc',
    'nok4s_acc',
    'nok6r_acc',
    'nok6s_acc',
    'nok7r_acc',
    'nok7s_acc',
    'nok8r_acc',
    'nok8s_acc',
    'nok9r_acc',
    'nok9s_acc',
    'zb2_acc',
    'zb3r_acc',
    'zb3s_acc',
    'bs1s_acc',
    'bs1r_acc',
    ]

wi = 80
he = 45
_plot1_1 = Column(
    Block('History motor %d%s' % (Time_selection1[0], Time_selection1[1]) , [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=wi,
                  height=he,
                  plotwindow=Time_selection1[0]*Time_selection1[2],
                  devices=Elemente1,
                  names=Elemente1,
                  legend=True),
        ),
        ],
    ),
)
_plot1_2 = Column(
    Block('History motor %d%s' % (Time_selection2[0], Time_selection2[1]) , [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=wi,
                  height=he,
                  plotwindow=Time_selection2[0]*Time_selection2[2],
                  devices=Elemente1,
                  names=Elemente1,
                  legend=True),
        ),
        ],
    ),
)
_plot2_1 = Column(
    Block('History acc %d%s' % (Time_selection1[0], Time_selection1[1]) , [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=wi,
                  height=he,
                  plotwindow=Time_selection1[0]*Time_selection1[2],
                  devices=Elemente2,
                  names=Elemente2,
                  legend=True),
        ),
        ],
    ),
)
_plot2_2 = Column(
    Block('History acc %d%s' % (Time_selection2[0], Time_selection2[1]) , [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=wi,
                  height=he,
                  plotwindow=Time_selection2[0]*Time_selection2[2],
                  devices=Elemente2,
                  names=Elemente2,
                  legend=True),
        ),
        ],
    ),
)

plot4x4 = [
        Row(_plot1_1, _plot1_2),
        Row(_plot2_1, _plot2_2),
        ]

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        showwatchdog = False,
        title = description,
        loglevel = 'info',
        cache = 'refsansctrl.refsans.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 12,
        padding = 5,
        layout = plot4x4,
    ),
)
