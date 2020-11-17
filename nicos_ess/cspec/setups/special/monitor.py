description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='Title', key='exp/title', width=20, istext=True,
                  maxlen=20),
            Field(name='Current status', key='exp/action', width=40,
                  istext=True, maxlen=40),
            Field(name='Last file', key='exp/lastscan'),
        ),
        ],
    ),
)

_plotcolumn = Column(
    Block('ERIC', [
        BlockRow(
            Field(dev='power'),
            Field(dev='ecurrent'),
        ),
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=40, height=40, plotwindow=1800,
                  devices=['power'],
                  legend=False),
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=40, height=40, plotwindow=1800,
                  devices=['ecurrent'],
                  legend=False,
            ),
        ),
        ],
    ),
)

_instrumentcolumn = Column(
    Block('CSPEC', [
        BlockRow(
            Field(dev='monolithshutter'),
            Field(dev='gammashutter'),
        ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'NICOS status monitor',
        loglevel = 'info',
        # Use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the hostname (official
        # computer name) or an IP address.
        cache = 'localhost',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        padding = 0,
        layout = [
            Row(_expcolumn),
            Row(_instrumentcolumn),
            Row(_plotcolumn),
        ],
    ),
)
