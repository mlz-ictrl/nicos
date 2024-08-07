description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=60,
                       istext=True, maxlen=60),
                 Field(name='Sample', key='sample/samplename', width=20),
                 ),
        BlockRow(Field(name='Current status', key='exp/action', width=60,
                       istext=True, maxlen=60),
                 Field(name='Last file', key='exp/lastscan'),
                ),
        ],
    ),
)

_axisblock = Block('Axes angles', [
    BlockRow(Field(name='Monochromator', key='mono/alias'), 'mono_stat'),
    BlockRow('mth', 'mtt'),
    BlockRow(Field(name='Focus mono', key='mono/focmode'), 'mfhpg', 'mfvpg'),
    BlockRow('psi', 'phi'),
    BlockRow('ath', 'att'),
    BlockRow(Field(name='Analyzer', key='ana/alias'),
             Field(name='Focus ana', key='ana/focmode'),
             'afpg'),
    ],
    # setups='puma',  # this is the name of a setup that must be loaded in the
                      # NICOS master instance for this block to be displayed
)

_sampletable = Block('Sampletable', [
    BlockRow('sgx','sgy'),
    BlockRow('stx','sty','stz'),
    ],
)

_slits = Block('Slits', [
    BlockRow(Field(name='left', dev='ss1_l'),
             Field(name='right', dev='ss1_r'),
             Field(name='bottom', dev='ss1_b'),
             Field(name='top', dev='ss1_t'),
            ),
    BlockRow(Field(name='left', dev='ss2_l'),
             Field(name='right', dev='ss2_r'),
             Field(name='bottom', dev='ss2_b'),
             Field(name='top', dev='ss2_t'),
            ),
    ],
)

_detectorblock = Block('Detector', [
    BlockRow(Field(name='timer', dev='timer'),
             Field(name='mon1', dev='mon1'),
             Field(name='Preset', key='mon1/preselection'),
             # Field(name='hvmonitor', dev='hvmonitor'),
            ),
    BlockRow(Field(name='det1', dev='det1'),
             Field(name='det2', dev='det2'),
             Field(name='det3', dev='det3'),
             # Field(name='hvdetector', dev='hv1detector')
            ),
    ],
)

_tasblock = Block('Triple-axis', [
    BlockRow(Field(dev='puma[0]', name='H', format='%.3f', unit=' '),
             Field(dev='puma[1]', name='K', format='%.3f', unit=' '),
             Field(dev='puma[2]', name='L', format='%.3f', unit=' '),
             Field(dev='puma[3]', name='E', format='%.3f', unit=' ')),
    BlockRow(Field(key='puma/scanmode', name='Mode'),
             Field(dev='mono', name='ki'),
             Field(dev='ana', name='kf'),
             Field(key='puma/energytransferunit', name='Unit')),
    BlockRow(Field(widget='nicos.guisupport.tas.TasWidget',
                   width=40, height=30, mthdev='mth', mttdev='mtt',
                   sthdev='psi', sttdev='phi', athdev='ath', attdev='att',
                  )
            ),
    ],
    setups='tas',
)

_multiblock = Block('', [
        BlockRow(
            Field(widget='nicos_mlz.puma.gui.multiwidget.MultiAnalyzerWidget',
                  width=40, heigth=30),
        ),
    ],
    setups='not tas',
)

# _shutterblock = Block('Shutter / Filters', [
#     BlockRow(Field(name='sapphire filter', dev='sapphire'),
#              Field(name='erbium filter', dev='erbium'),),
#     BlockRow(Field(name='attenuator', dev='atn'),
#              Field(name='PG filter 1', dev='fpg1'),
#              Field(name='PG filter 2', dev='fpg2'),
#             ),
#     ],
# )

_reactor = Block('Reactor power', [
    BlockRow(Field(dev='ReactorPower')),
    ],
)

# _collimationblock = Block('Collimation', [
#     BlockRow(Field(name='alpha1', dev='alpha1'),
#              Field(name='alpha2', dev='alpha2'),
#              Field(name='alpha3', dev='alpha3'),
#              Field(name='alpha4', dev='alpha4'),
#             ),
#     ],
# )

_leftcolumn = Column(_tasblock, _multiblock, _detectorblock, _reactor)
_middlecolumn = Column(_axisblock, _sampletable, _slits)
_rightcolumn = Column(
    #_shutterblock, _collimationblock,
)


devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'NICOS status monitor',
        loglevel = 'info',
        cache = configdata('config_data.host'),
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        padding = 0,
        layout = [Row(_expcolumn),
                  Row(_leftcolumn, _middlecolumn, _rightcolumn)
                 ],
    ),
)
