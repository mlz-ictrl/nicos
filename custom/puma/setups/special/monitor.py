description = 'setup for the status monitor'
group = 'special'

Row = Column = Block = BlockRow = lambda *args: args
Field = lambda *args, **kwds: args or kwds

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=40,
                       istext=True, maxlen=40),
                 Field(name='Last file', key='filesink/lastfilenumber'))]),
)

_axisblock = Block(
    'Axes',
    [
     BlockRow('mth', 'mtt'),
     BlockRow('psi', 'phi'),
     BlockRow('ath', 'att'),
    ],
    'puma')  # this is the name of a setup that must be loaded in the
            # NICOS master instance for this block to be displayed

_sampletable = Block(
    'Sampletable',
    [
     BlockRow('sgx','sgy'),
     BlockRow('sat'),
    ],
)

_detectorblock = Block(
    'Detector',
    [BlockRow(Field(name='timer', dev='timer'),
              Field(name='mon1',  dev='mon1'),
              Field(name='mon2',  dev='mon2')
	      ),
     BlockRow(Field(name='det1',  dev='det1'),
              Field(name='det2',  dev='det2'),
              Field(name='det3',  dev='det3'),
              Field(name='det4',  dev='det4'),
              Field(name='det5',  dev='det5'),
	      ),
    ],
)

_tasblock = Block(
    'Triple-axis',
    [BlockRow(Field(dev='puma', item=0, name='H', format='%.3f', unit=' '),
              Field(dev='puma', item=1, name='K', format='%.3f', unit=' '),
              Field(dev='puma', item=2, name='L', format='%.3f', unit=' '),
              Field(dev='puma', item=3, name='E', format='%.3f', unit=' ')),
     BlockRow(Field(key='puma/scanmode', name='Mode'),
              Field(dev='mono', name='ki', min=1.55, max=1.6),
              Field(dev='ana', name='kf'),
              Field(key='puma/energytransferunit', name='Unit')),
     BlockRow(Field(widget='nicos.demo.monitorwidgets.VTas',
                    width=40, height=30,
                    fields={'mth': 'mth',
                            'mtt': 'mtt',
                            'sth': 'psi',
                            'stt': 'phi',
                            'ath': 'ath',
                            'att': 'att',
                            'tas': 'puma'})),
    ],
    'puma')

_tempblock = Block(
    'Temperature',
    [BlockRow(Field(name='Control',dev='t_ls340'), Field(key='t_ls340/setpoint', name='Setpoint')),
     BlockRow(Field(name='ChannelA',dev='t_ls340_a'),
              Field(name='ChannelB',dev='t_ls340_b')),


#     BlockRow(Field(dev='T', plot='T', interval=300, width=50),
#              Field(key='t/setpoint', name='SetP', plot='T', interval=300))
    ],
    'lakeshore')


_leftcolumn = Column(_axisblock, _sampletable)
_middlecolumn = Column(_detectorblock, _tempblock)
_rightcolumn = Column(_tasblock)


devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     cache = 'pumahw:14869',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 0,
                     layout = [Row(_expcolumn), Row(_leftcolumn, _middlecolumn, _rightcolumn)],
                     notifiers = [])
)
