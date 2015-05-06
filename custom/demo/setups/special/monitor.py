description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=40,
                       istext=True, maxlen=40),
                 Field(name='Last scan file', key='exp/lastscan'),
                )
        ],
        setups='tas',
    ),
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=40,
                       istext=True, maxlen=40),
                 Field(name='Last Image file', key='exp/lastimage'),
                ),
        ],
        setups='sans or refsans',
    ),
)

_axisblock = Block('Axes', [
    BlockRow(Field(gui='custom/demo/lib/gui/tasaxes.ui')),
#   BlockRow('mth', 'mtt'),
#   BlockRow('psi', 'phi'),
#   BlockRow('ath', 'att'),
    ],
    setups='tas',  # this is the name of a setup that must be loaded in the
                   # NICOS master instance for this block to be displayed
)

_refsansblock = Block('Axes', [
        BlockRow(Field(gui='custom/demo/lib/gui/refsansflightchamber.ui')),
        BlockRow(Field(widget='nicos.refsans.monitorwidgets.VRefsans',
                       width=40, height=30,
                       nok2dev='nok2',
                       nok3dev='nok3',
                       nok4dev='nok4',
                       nok5adev='nok5a',
                       nok5bdev='nok5b',
                       nok6dev='nok6',
                       nok7dev='nok7',
                       nok8dev='nok8',
                      )),
    ],
    setups='refsans',
)

_detectorblock = Block('Detector', [
    BlockRow(Field(name='timer', dev='timer'),
             Field(name='ctr1',  dev='ctr1'),
             Field(name='ctr2',  dev='ctr2')),
    ],
    setups='detector',
)

_tasblock = Block('Triple-axis', [
    BlockRow(Field(dev='tas', item=0, name='H', format='%.3f', unit=' '),
             Field(dev='tas', item=1, name='K', format='%.3f', unit=' '),
             Field(dev='tas', item=2, name='L', format='%.3f', unit=' '),
             Field(dev='tas', item=3, name='E', format='%.3f', unit=' ')),
    BlockRow(Field(key='tas/scanmode', name='Mode'),
             Field(dev='mono', name='ki', min=1.55, max=1.6),
             Field(dev='ana', name='kf'),
             Field(key='tas/energytransferunit', name='Unit')),
    BlockRow(Field(widget='nicos.demo.monitorwidgets.VTas',
                   width=40, height=30,
                   mthdev = 'mth',
                   mttdev = 'mtt',
                   sthdev = 'psi',
                   sttdev = 'phi',
                   athdev = 'ath',
                   attdev = 'att')),
    ],
    setups='tas',
)

_tempblock = Block('Temperature', [
    BlockRow(Field(gui='custom/demo/lib/gui/cryo.ui')),
#   BlockRow(Field(dev='T'), Field(key='t/setpoint', name='Setpoint')),
#   BlockRow(Field(dev='T', plot='T', plotwindow=300, width=50),
#            Field(key='t/setpoint', name='SetP', plot='T', plotwindow=300))
    ],
    setups='cryo',
)

_sansblock = Block('SANS', [
    BlockRow(
        Field(dev='guide1', name='G1',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['off','ng','P3','P4'],
              #~ options=['off','ng'],#'P3','P4'],
              width=4,height=5),
        Field(dev='guide2', name='G2',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['off','ng','P3','P4'],
              #~ options=['off','ng'],#'P3','P4'],
              width=4,height=5),
        Field(dev='guide3', name='G3',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['off','ng','P3','P4'],
              #~ options=['off','ng'],#'P3','P4'],
              width=4,height=5),
        Field(dev='guide4', name='G4',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['off','ng','P3','P4'],
              #~ options=['off','ng'],#'P3','P4'],
              width=4,height=5),
        #~ Field(dev='det_pos', name='Detector position',
              #~ widget='nicos.sans1.monitorwidgets.Tube', width=30, height=10)),
        Field(devices=['det_pos1', 'det_pos1_x','det_pos1_tilt', 'det_pos2'],
                name='Detector position',
                widget='nicos.sans1.monitorwidgets.Tube2', width=30, height=10, posscale=21)
    ),
    BlockRow(
        Field(dev='guide', name='Guide',
              widget='nicos.sans1.monitorwidgets.BeamOption',
              width=10, height=4),
        Field(dev='det_HV', name='Detector HV', format='%d'),
        Field(key='det/lastcounts', name='Counts on det', format='%d')
    ),
    ],
    setups='sans',
)

_pgaablock = Block( 'PGAA', [
    BlockRow(
        Field(dev='x', name='X',
             ),
        Field(dev='y', name='Y',
             ),
        Field(dev='z', name='Z',
             ),
        Field(dev='phi', name='Phi',
             ),
    ),
    ],
    setups='pgaa',
)

_pgaacolumn = Column(_pgaablock)

_rightcolumn = Column(_axisblock, _tempblock,)

_leftcolumn = Column(_tasblock, _sansblock, _refsansblock,)

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     cache = 'localhost:14869',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 0,
                     colors = 'light',
                     layout = [Row(_expcolumn), Row(_leftcolumn,_rightcolumn,),
                               Row(_pgaacolumn),],
                    ),
)
