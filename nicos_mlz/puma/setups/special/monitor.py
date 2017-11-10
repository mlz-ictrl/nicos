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
    BlockRow(Field(name='Monochromator', key='mono/alias'),'mono_stat'),
    BlockRow('mth', 'mtt'),
    BlockRow(Field(name='Focus mono', key='mono/focmode'),'mfhcu','mfvcu'),
    BlockRow('psi', 'phi'),
    BlockRow('ath', 'att'),
    BlockRow(Field(name='Analyzer', key='ana/alias'),
             Field(name='Focus ana', key='ana/focmode'),
             'afpg'),
    ],
    setups='puma',  # this is the name of a setup that must be loaded in the
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
             Field(name='Preset', key='mon1/preselection'), #'mon1/value'/'mon1/preselection'*'det2/value' 'mon1/preselection'
            ),
    BlockRow(Field(name='det1', dev='det1'),
             Field(name='det2', dev='det2'),
             Field(name='det3', dev='det3'),
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
    setups='puma',
)



_shutterblock = Block('Shutter / Filters', [
    BlockRow(Field(name='alpha1', dev='alpha1'),
             Field(name='sapphire filter',  dev='sapphire'),
             Field(name='erbium filter',  dev='erbium'),),
    BlockRow(Field(name='attenuator', dev='atn'),
             Field(name='PG filter 1',  dev='fpg1'),
             Field(name='PG filter 2',  dev='fpg2'),
            ),
    ],
)

_reactor = Block('Reactor power', [
    BlockRow(Field(dev='ReactorPower')),
    ],
)

_leftcolumn = Column(_tasblock, _detectorblock, _reactor)
_middlecolumn = Column(_axisblock, _sampletable, _slits)
_rightcolumn = Column(_shutterblock,
    Block('Temperature (LakeShore)', [
        BlockRow(Field(name='Control',dev='t_ls340'),
            Field(key='t_ls340/setpoint', name='Setpoint')),
        BlockRow(Field(name='Ts',dev='t_ls340_b'),
                 Field(name='Heater power', key='t_ls340/heaterpower')),
        BlockRow(Field(dev='T', plot='T', plotwindow=1800, width=40),
                 Field(key='ts', name='Sample T', plot='T', plotwindow=1800),
                 Field(key='t/setpoint', name='SetP', plot='T', plotwindow=1800))
    ], setups='lakeshore'),
    Block('Temperature (CCR18)', [
        BlockRow(Field(name='T_tube',dev='t_ccr18_tube'),
                 Field(key='t_ccr18_tube/setpoint', name='Setpoint_tube'),
                 Field(key='t_ccr18_tube/heaterpower',name='heaterpower_tube')),
        BlockRow(Field(name='T_tube',key='T_ccr18_tube', plot='T',
                       plotwindow=3600, width=40),
                 Field(key='t_ccr18_tube/setpoint', name='SetP', plot='T',
                       plotwindow=3600, width=40)),
    ], setups='ccr18'),
    Block('Temperature (CCR16)', [
        BlockRow(Field(name='T_stick',dev='t_ccr16_stick'),
                 Field(key='t_ccr16_stick/setpoint', name='Setpoint_stick'),
                 Field(key='t_ccr16_stick/heaterpower',name='heaterpower_stick')),
        BlockRow(Field(name='Pressure',dev='ccr16_p1'),
                 Field(name='Coldhead',dev='T_ccr16_C'),
                 Field(name='compressor',dev='ccr16_compressor'),
                 Field(name='vacuum',dev='ccr16_vacuum_switch')),
        BlockRow(Field(name='T_stick',dev='T_ccr16_stick', plot='T',
                       plotwindow=3600, width=40)),
    ], setups='ccr16'),
)


devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     cache = 'pumahw.puma.frm2:14869',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 0,
                     layout = [Row(_expcolumn), Row(_leftcolumn, _middlecolumn,
                               _rightcolumn)],
                    ),
)
