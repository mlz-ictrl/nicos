description = 'setup for the status monitor'
group = 'special'

Row = Column = BlockRow = lambda *args: args
Block = lambda *args, **kwds: (args, kwds)
Field = lambda *args, **kwds: args or kwds

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

_axisblock = Block('Axes angles', [
    BlockRow(Field(name='Monochromator'),'mono_stat'),
    BlockRow('mth', 'mtt'),
    BlockRow(Field(name='Focus mono', key='mono/focmode'),'mfhpg'),
    BlockRow('psi', 'phi'),
    BlockRow('ath', 'att'),
    BlockRow(Field(name='Focus ana', key='ana/focmode'),'afpg'),
    ],
    setups='puma',  # this is the name of a setup that must be loaded in the
                    # NICOS master instance for this block to be displayed
)

_sampletable = Block('Sampletable', [
    BlockRow('sgx','sgy'),
    BlockRow('stx','sty','stz'),
    BlockRow('atn','fpg1','fpg2'),
    ],
)

_slits = Block('Slits', [
#   BlockRow('slit1.left','slit1.right','slit1.bottom','slit1.top'),
#   BlockRow('slit2.left','slit2.right','slit2.bottom','slit2.top')
    BlockRow(Field(name='left',dev='ss1_l'),
              Field(name='right',dev='ss1_r'),
              Field(name='bottom',dev='ss1_b'),
              Field(name='top',dev='ss1_t'),
             ),
    BlockRow(Field(name='left',dev='ss2_l'),
              Field(name='right',dev='ss2_r'),
              Field(name='bottom',dev='ss2_b'),
              Field(name='top',dev='ss2_t'),
             ),
    ],
)

_detectorblock = Block('Detector', [
    BlockRow(Field(name='timer', dev='timer'),
             Field(name='mon1',  dev='mon1'),
             Field(name='mon2',  dev='mon2'),
            ),
    BlockRow(Field(name='det1',  dev='det1'),
             Field(name='det2',  dev='det2'),
             Field(name='det3',  dev='det3'),
             Field(name='det4',  dev='det4'),
             Field(name='det5',  dev='det5'),
            ),
    ],
)

_tasblock = Block('Triple-axis', [
    BlockRow(Field(dev='puma', item=0, name='H', format='%.3f', unit=' '),
             Field(dev='puma', item=1, name='K', format='%.3f', unit=' '),
             Field(dev='puma', item=2, name='L', format='%.3f', unit=' '),
             Field(dev='puma', item=3, name='E', format='%.3f', unit=' ')),
    BlockRow(Field(key='puma/scanmode', name='Mode'),
             Field(dev='mono', name='ki'),
             Field(dev='ana', name='kf'),
             Field(key='puma/energytransferunit', name='Unit')),
#   BlockRow(Field(widget='nicos.demo.monitorwidgets.VTas',
#                  width=40, height=30,
#                  fields={'mth': 'mth',
#                          'mtt': 'mtt',
#                          'sth': 'psi',
#                          'stt': 'phi',
#                          'ath': 'ath',
#                          'att': 'att',
#                          'tas': 'puma'})),
    ],
    setups='puma',
)

_tempblock = Block('Temperature', [
    BlockRow(Field(name='Control',dev='t_ls340'), Field(key='t_ls340/setpoint', name='Setpoint')),
    BlockRow(Field(name='ChannelA',dev='t_ls340_a'),
              Field(name='ChannelB',dev='t_ls340_b')),
#   BlockRow(Field(dev='T', plot='T', plotwindow=300, width=50),
#            Field(key='t/setpoint', name='SetP', plot='T', plotwindow=300))
    ],
    setups='lakeshore',
)

_shutterblock = Block('Shutter', [
    BlockRow(Field(name='alpha1', dev='alpha1'),
             Field(name='sapphire filter',  dev='sapphire'),
             Field(name='erbium filter',  dev='erbium'),
            ),
    ],
)

_reactor = Block('Reactor power', [
    BlockRow(Field(dev='ReactorPower')),
    ],
)

_leftcolumn = Column(_axisblock, _sampletable)
_middlecolumn = Column(_shutterblock,_detectorblock, _tempblock)
_rightcolumn = Column(_tasblock, _slits,_reactor)


devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     cache = 'pumahw:14869',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 0,
                     layout = [Row(_expcolumn), Row(_leftcolumn, _middlecolumn, _rightcolumn)],
                    ),
)
