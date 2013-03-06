description = 'setup for the status monitor'
group = 'special'

Row = Column = Block = BlockRow = lambda *args: args
Field = lambda *args, **kwds: args or kwds

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=30,
                       istext=True),
                 Field(name='Last file', key='filesink/lastfilenumber'))]),
)

_axisblock = Block(
    'Axes',
    [BlockRow('mth', 'mtt'),
     BlockRow('psi', 'phi'),
     BlockRow('ath', 'att'),
    ],
    'tas')  # this is the name of a setup that must be loaded in the
            # NICOS master instance for this block to be displayed

_detectorblock = Block(
    'Detector',
    [BlockRow(Field(name='timer', dev='timer'),
              Field(name='ctr1',  dev='ctr1', min=100, max=500),
              Field(name='ctr2',  dev='ctr2')),
    ],
    'detector')

_tasblock = Block(
    'Triple-axis',
    [BlockRow(Field(dev='tas', item=0, name='H', format='%.3f', unit=''),
              Field(dev='tas', item=1, name='K', format='%.3f', unit=''),
              Field(dev='tas', item=2, name='L', format='%.3f', unit=''),
              Field(dev='tas', item=3, name='E', format='%.3f', unit='')),
     BlockRow(Field(key='tas/scanmode', name='Mode'),
              Field(dev='mono', name='ki'),
              Field(dev='ana', name='kf'),
              Field(key='tas/energytransferunit', name='Unit')),
     BlockRow(Field(multiwidget='nicos.demo.monitorwidgets.VTas',
                    width=40, height=30,
                    fields={'mth': 'mth',
                            'mtt': 'mtt',
                            'sth': 'psi',
                            'stt': 'phi',
                            'ath': 'ath',
                            'att': 'att',
                            'tas': 'tas'})),
    ],
    'tas')

_tempblock = Block(
    'Temperature',
    [BlockRow(Field(dev='T'), Field(key='t/setpoint', name='Setpoint')),
#     BlockRow(Field(dev='T', plot='T', interval=300, width=50),
#              Field(key='t/setpoint', name='SetP', plot='T', interval=300))
    ],
    'temperature')

_rightcolumn = Column(_axisblock, _detectorblock)

_leftcolumn = Column(_tasblock)#, _tempblock)

_sansblock = Block(
    'SANS',
    [BlockRow(
        Field(dev='guide', name='Guide', widget='nicos.sans1.monitorwidgets.BeamOption',
              width=10, height=4),
        Field(dev='coll', name='Collimation', widget='nicos.sans1.monitorwidgets.BeamOption',
              width=10, height=4),
        Field(dev='tube', name='Tube', widget='nicos.sans1.monitorwidgets.Tube', width=30, height=10)),
    ],
    'sans')

_sanscolumn = Column(_sansblock)


devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     cache = 'localhost:14869',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 0,
                     layout = [Row(_expcolumn), Row(_rightcolumn, _leftcolumn),
                               Row(_sanscolumn)],
                     notifiers = [])
)
