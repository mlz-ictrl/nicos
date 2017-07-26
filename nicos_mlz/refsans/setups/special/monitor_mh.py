description = 'REFSANS status monitor'
group = 'special'

_experimentcol = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='Title',    key='exp/title',    width=20,
                istext=True, maxlen=20),
            Field(name='Sample name', key='sample/samplename', width=16),
            Field(name='User name', key='exp/username',    width=20,
                istext=True, maxlen=20),
            Field(name='Last file', key='det/lastfilenumber'),
            Field(name='Last point', key='exp/lastpoint'),
            ),
        BlockRow(
            Field(name='Remark',   key='exp/remark',   width=40,
                istext=True, maxlen=40),
            Field(name='Current status', key='exp/action', width=50,
                istext=True, maxlen=40),
            )
        ],
    ),
)

_generalcol = Column(
    Block('General', [
        BlockRow(
            Field(name='Reactor', dev='ReactorPower', width=12),
            Field(name='6-fold shutter', dev='Sixfold', width=12),
            Field(name='NL2b', dev='NL2b', width=12),
            Field(name='Shutter', dev='shutter', width=12),
            Field(name='nok1', dev='nok1', width=12),
            Field(name='Crane', dev='Crane', width=12),
            Field(name='fak40', dev='fak40', width=8),
            ),
        BlockRow(
            Field(name='T in', dev='t_memograph_in', width=12, unit='C'),
            Field(name='T out', dev='t_memograph_out', width=12, unit='C'),
            Field(name='Cooling', dev='cooling_memograph', width=12,
                  unit='kW'),
            ),
        ],
    ),
)


devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
                     title = description,
                     loglevel = 'info',
                     cache = 'refsansctrl01.refsans.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 12,
                     padding = 5,
                     layout = [
                               Row(_experimentcol),
                               Row(_generalcol),
                              ],
                    ),
)
