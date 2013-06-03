#  -*- coding: utf-8 -*-

name = 'setup for the status monitor'
group = 'special'

Row = Column = Block = BlockRow = lambda *args: args
Field = lambda *args, **kwds: args or kwds

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='Title', key='exp/title', width=40, istext=True),
            Field(name='Current status', key='exp/action', width=30, istext=True),
            Field(name='Last file', key='filesink/lastfilenumber'),
            ),
        ],
    ),
)

_axisblock = Block('Axis devices', [
    BlockRow(
        Field(dev='a1'), Field(dev='m1'), Field(dev='c1'),
        ),
    BlockRow(
        Field(dev='a2'), Field(dev='m2'),
        ),
    ], 
    'misc',
)

_detectorblock = Block('Detector devices', [
    BlockRow(
        Field(dev='timer'), Field(dev='ctr1'), Field(dev='ctr2'),
        ),
    ],
    'detector',
)

_otherblock = Block('Other devices', [
    BlockRow(
        Field(dev='slit', name='Slit', width=20),
        ),
    BlockRow(
        Field(dev='sw', name='Switcher', width=4),
        ),
    BlockRow(
        Field(dev='freq', name='Frequency'),
        Field(key='freq/amplitude', name='Amplitude', unit='mV'),
        ),
    ],
    'misc',
)

_rightcolumn = Column(
    _axisblock,
    _detectorblock,
)

_leftcolumn = Column(
    _otherblock,
)

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                      description = 'Status Display',
                      title = 'Test status monitor',
                      loglevel = 'info',
                      cache = 'antareshw.antares.frm2',
                      prefix = 'nicos/',
                      font = 'Luxi Sans',
                      valuefont = 'Monospace',
                      padding = 5,
                      layout = [[_expcolumn], [_rightcolumn, _leftcolumn]],
                    ),
)
