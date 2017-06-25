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
                 Field(name='Last file', key='exp/lastscan'),
                ),
        ],
    ),
)

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     cache = 'nectarhw.nectar.frm2',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 0,
                     layout = [Row(_expcolumn)],
                    ),
)
