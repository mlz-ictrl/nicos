description = 'setup for the status monitor for PGAA'
group = 'special'


_pressuresample = Block('Sample ', [
    BlockRow(Field(name='Vacuum', dev='sample_p1'),
            ),
    ],  # setups = '',
)

_leftcolumn = [
    _pressuresample,
]

_rightcolumn = [
]

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'PGAA status monitor',
                     loglevel = 'info',
                     cache = 'tequila.pgaa.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 16,
                     padding = 5,
                     layout = [
                                  [[_pressuresample,],]
#                                 [_leftcolumn, _rightcolumn, ]
                              ],
                    ),
)
