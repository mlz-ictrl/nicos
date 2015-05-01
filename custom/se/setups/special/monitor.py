description = 'setup for the status monitor'
group = 'special'

_expcolumn = [
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title', key='exp/title', width=30, istext=True,
                       maxlen=40),
                 Field(name='Sample', key='sample/samplename', width=30, istext=True),
                 Field(name='Remark', key='exp/remark', width=30, istext=True),
                )
        ],
    ),
]

_reactorblock = Block('Reactor', [
    BlockRow(Field(name='Power', dev='ReactorPower'), ),
    ]
)

_col1 = [
    _reactorblock,
]

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     cache = 'localhost:14869',
                     prefix = 'nicos/',
                     font = 'Ubuntu',
                     valuefont = 'DejaVu Sans Mono',
                     padding = 5,
                     layout = [[_expcolumn], [_col1, ]],
                    ),
)
