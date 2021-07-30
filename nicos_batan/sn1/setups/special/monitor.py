description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='Title',    key='exp/title',    width=20, istext=True,
                  maxlen=20),
            Field(name='Current status', key='exp/action', width=40,
                  istext=True, maxlen=40),
            Field(name='Last scan file', key='exp/lastscan',
                  setups='sn1'),
        )
    ],
    ),
)

_axisblock = Block('Axes', [
    BlockRow(Field(gui='nicos/clients/gui/panels/tasaxes.ui')),
    # BlockRow('mth', 'mtt'),
    # BlockRow('psi', 'phi'),
    # BlockRow('ath', 'att'),
    ],
    setups='sn1',  # this is the name of a setup that must be loaded in the
                   # NICOS master instance for this block to be displayed
)

_detectorblock = Block('Detector', [
    BlockRow(Field(name='timer', dev='timer'),
             Field(name='ctr1',  dev='ctr1'),
             Field(name='ctr2',  dev='ctr2')),
    ],
    setups='detector',
)

_tasblock = Block('Triple-axis', [
    BlockRow(Field(dev='SN1[0]', name='H', format='%.3f', unit=' '),
             Field(dev='SN1[1]', name='K', format='%.3f', unit=' '),
             Field(dev='SN1[2]', name='L', format='%.3f', unit=' '),
             Field(dev='SN1[3]', name='E', format='%.3f', unit=' ')),
    BlockRow(Field(key='sn1/scanmode', name='Mode'),
             Field(dev='mono', name='ki', min=1.55, max=1.6),
             Field(dev='ana', name='kf'),
             Field(key='sn1/energytransferunit', name='Unit')),
    BlockRow(Field(widget='nicos.guisupport.tas.TasWidget',
                   width=40, height=30,
                   mthdev='mth',
                   mttdev='mtt',
                   sthdev='psi',
                   sttdev='phi',
                   athdev='ath',
                   attdev='att',
                   Lmsdev='Lms',
                   Laddev='Lad',
                   Lsadev='Lsa',
                   tasdev='SN1',)),
    ],
    setups='sn1',
)

_slitblock = Block('Sample Slit', [
    BlockRow(Field(dev='ss', name='Sample slit')),
    BlockRow(Field(dev='ss.height', name='Height'),
             Field(dev='ss.width', name='Width')),
    ],
    setups='sn1',
)

_rightcolumn = Column(_axisblock)

_leftcolumn = Column(_tasblock, _slitblock)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'NICOS status monitor',
        loglevel = 'info',
        cache = 'localhost:14869',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        padding = 0,
        colors = 'light',
        layout = [
            Row(_expcolumn),
            Row(_leftcolumn, _rightcolumn),
        ],
    ),
)
