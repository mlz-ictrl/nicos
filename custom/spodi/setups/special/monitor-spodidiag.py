# This setup file configures the nicos status monitor.

description = 'setup for the status monitor'
group = 'special'

_expblock = Block('Experiment', [
    BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
             Field(name='Title',    key='exp/title',    width=20,
                   istext=True, maxlen=20),
             Field(name='Current status', key='exp/action', width=40,
                   istext=True, maxlen=40),
             Field(name='Last file', key='exp/lastscan'))])


_ngpressblock = Block('Neutron guide pressure', [
    BlockRow(
             Field(name='Pressure 1', dev='p1_nguide'),
             Field(name='Pressure 2', dev='p2_nguide'),
             Field(name='Pressure 3', dev='p3_nguide'),
    ),
    BlockRow(
             Field(widget='nicos.guisupport.plots.TrendPlot',
                 devices=['p1_nguide', 'p2_nguide', 'p3_nguide'],
                 names=['Pressure 1', 'Pressure 2', 'Pressure 3'],
                 legend=True,
                 plotwindow=7*24*3600,
                 height=35,
                 width=38),
    ),
    ])


_ngo2block = Block('Neutron guide oxygen', [
    BlockRow(
             Field(name='O2', dev='o2_nguide'),
             Field(name='O2 part', dev='o2part_nguide'),
    ),
    BlockRow(
             Field(widget='nicos.guisupport.plots.TrendPlot',
                 devices=['o2_nguide'],
                 names=['O2 content'],
                 legend=True,
                 plotwindow=7*24*3600,
                 height=35,
                 width=38),
    ),
    ])


_ngtempblock = Block('Neutron guide', [
    BlockRow(
             Field(name='Temperature', dev='T_nguide'),
    ),
    BlockRow(
             Field(widget='nicos.guisupport.plots.TrendPlot',
                 devices=['T_nguide'],
                 names=['Temperature'],
                 legend=True,
                 plotwindow=7*24*3600,
                 height=35,
                 width=38),
    ),
    ])


_expcolumn = Column(
    _expblock
)

_ngpresscolumn = Column(
    _ngpressblock
)

_ngo2column = Column(
    _ngo2block
)

_ngtempcolumn = Column(
    _ngtempblock
)


devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     # Use only 'localhost' if the cache is really running on
                     # the same machine, otherwise use the hostname (official
                     # computer name) or an IP address.
                     cache = 'spodictrl.spodi.frm2',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 0,
                     fontsize = 15,
                     layout = [Row(_expcolumn), Row(_ngpresscolumn, _ngo2column, _ngtempcolumn)],
                    ),
)
