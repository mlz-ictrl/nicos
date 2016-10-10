# This setup file configures the nicos status monitor.

description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=40,
                       istext=True, maxlen=40),
                 Field(name='Last file', key='exp/lastscan'))]),
)

_sampletable = Block('Sample table', [
    BlockRow(
        Field(dev='xt', format='%.1f'),
        Field(dev='yt'),
        Field(dev='zt',format='%.2f'),
        Field(dev='omgs'),
        Field(dev='tths'),
    ),
    ],
    setups = 'sampletable',
)

_eulerian = Block('Eulerian', [
     BlockRow(
        Field(dev='chis'),
        Field(dev='phis'),
    )
    ],
    setups = 'eulerian*',
)

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     # Use only 'localhost' if the cache is really running on
                     # the same machine, otherwise use the hostname (official
                     # computer name) or an IP address.
                     cache = 'stressictrl.stressi.frm2',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 0,
                     layout = [Row(_expcolumn), Row(Column(_sampletable)), Row(Column(_eulerian))],
                    ),
)
