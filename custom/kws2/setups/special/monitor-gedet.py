# This setup file configures the nicos status monitor.

description = 'setup for the GE detector status monitor'
group = 'special'

_column1 = Column(
    Block('Temp. FPGA', [
        BlockRow(Field(dev='ep%02d_T' % ep, name='ep%d' % ep),
                 Field(dev='ep%02d_T' % (ep + 9), name='ep%d' % (ep + 9)),
        ) for ep in range(1, 10)]),
)

_column1b = Column(
    Block('Temp. RSPP', [
        BlockRow(Field(dev='ep%02d_TB' % ep, name='ep%d' % ep),
                 Field(dev='ep%02d_TB' % (ep + 9), name='ep%d' % (ep + 9)),
        ) for ep in range(1, 10)]),
)

_column2 = Column(
    Block('High voltage', [
        BlockRow(Field(dev='ep%02d_HV' % ep, name='ep%d' % ep),
                 Field(dev='ep%02d_HV' % (ep + 9), name='ep%d' % (ep + 9))
        ) for ep in range(1, 10)]),
)

_column3 = Column(
    Block('Temperature history', [
        BlockRow(Field(plot='Ts', dev='ep01_T', width=50, height=15, plotwindow=24*3600,
                       legend=False),
                 *[Field(plot='Ts', dev='ep%02d_T' % ep) for ep in range(2, 19)]),
    ]),
    Block('HV history', [
        BlockRow(Field(plot='HVs', dev='ep01_HV', width=50, height=15, plotwindow=24*3600),
                 *[Field(plot='HVs', dev='ep%02d_HV' % ep) for ep in range(2, 19)]),
    ])
)

_column4 = Column(
    Block('Power supply', [
        BlockRow(Field(dev='ps1_V'), Field(dev='ps1_I'),
                 Field(dev='ps2_V'), Field(dev='ps2_I')),
    ]),
)

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'KWS-2 GE detector status',
                     loglevel = 'info',
                     # Use only 'localhost' if the cache is really running on
                     # the same machine, otherwise use the hostname (official
                     # computer name) or an IP address.
                     cache = 'localhost',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 0,
                     noexpired = True,
                     layout = [Row(_column1, _column1b, _column2, _column3), Row(_column4)],
                    ),
)
