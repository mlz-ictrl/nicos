description = 'setup for the HTML status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='Title',    key='exp/title',    width=60,
                  istext=True, maxlen=60),
            Field(name='Sample', key='sample/samplename', width=20),
        ),
        BlockRow(
            Field(name='Current status', key='exp/action', width=60,
                  istext=True, maxlen=60),
            Field(name='Last file', key='exp/lastscan'),
        ),
        ],
    ),
)

_axisblock = Block('Axes angles', [
    BlockRow(
        Field(name='Monochromator', key='mono/alias'),
        Field(dev='mono_stat'),
    ),
    BlockRow(
        Field(dev='mth'),
        Field(dev='mtt'),
    ),
    BlockRow(
        Field(name='Focus mono', key='mono/focmode'),
        Field(dev='mfhpg'),
        Field(dev='mfvpg'),
    ),
    BlockRow(
        Field(dev='sth'),
        Field(dev='stt'),
    ),
    BlockRow(
        Field(dev='ath'),
        Field(dev='att'),
    ),
    BlockRow(
        Field(name='Analyzer', key='ana/alias'),
        Field(name='Focus ana', key='ana/focmode'),
        Field(dev='afpg'),
    ),
    ],
    # setups='puma',  # this is the name of a setup that must be loaded in the
                      # NICOS master instance for this block to be displayed
)

_sampletable = Block('Sampletable', [
    BlockRow(
        Field(dev='sgx'),
        Field(dev='sgy'),
    ),
    BlockRow(
        Field(dev='stx'),
        Field(dev='sty'),
        Field(dev='stz'),
    ),
    ],
)

_slits = Block('Slits', [
    BlockRow(
        Field(name='left', dev='ss1_l'),
        Field(name='right', dev='ss1_r'),
        Field(name='bottom', dev='ss1_b'),
        Field(name='top', dev='ss1_t'),
    ),
    BlockRow(
        Field(name='left', dev='ss2_l'),
        Field(name='right', dev='ss2_r'),
        Field(name='bottom', dev='ss2_b'),
        Field(name='top', dev='ss2_t'),
    ),
    ],
)

_detectorblock = Block('Detector', [
    BlockRow(
        Field(name='timer', dev='timer'),
        Field(name='mon1', dev='mon1'),
        Field(name='Preset', key='mon1/preselection'),
    ),
    BlockRow(
        Field(name='det1', dev='det1'),
        Field(name='det2', dev='det2'),
        Field(name='det3', dev='det3'),
    ),
    ],
)

_tasblock = Block('Triple-axis', [
    BlockRow(
        Field(key='puma/value[0]', name='H', format='%.3f', unit=' '),
        Field(key='puma/value[1]', name='K', format='%.3f', unit=' '),
        Field(key='puma/value[2]', name='L', format='%.3f', unit=' '),
        Field(key='puma/value[3]', name='E', format='%.3f', unit=' '),
    ),
    BlockRow(
        Field(key='puma/scanmode', name='Mode'),
        Field(dev='mono', name='ki'),
        Field(dev='ana', name='kf'),
        Field(key='puma/energytransferunit', name='Unit'),
    ),
    ],
    # setups='puma',
)

_shutterblock = Block('Shutter / Filters', [
    BlockRow(
        Field(name='alpha1', dev='alpha1'),
        Field(name='sapphire filter',  dev='sapphire'),
        Field(name='erbium filter',  dev='erbium'),
    ),
    BlockRow(
        Field(name='attenuator', dev='atn'),
        Field(name='PG filter 1',  dev='fpg1'),
        Field(name='PG filter 2',  dev='fpg2'),
    ),
    ],
)

_reactor = Block('Reactor power', [
    BlockRow(
        Field(dev='ReactorPower'),
    ),
    ],
)

_leftcolumn = Column(_tasblock, _detectorblock, _reactor)
_middlecolumn = Column(_axisblock, _sampletable, _slits)
_rightcolumn = Column(_shutterblock,
    Block('Temperature (LakeShore)', [
        BlockRow(
            Field(name='Control', dev='t_ls340'),
            Field(name='Setpoint', key='t_ls340/setpoint'),
        ),
        BlockRow(
            Field(name='Ts',dev='t_ls340_b'),
            Field(name='Heater power', key='t_ls340/heateroutput'),
        ),
        # BlockRow(
        #     Field(dev='T', plot='T', plotwindow=1800, width=40),
        #     Field(key='ts', name='Sample T', plot='T', plotwindow=1800),
        #     Field(key='t/setpoint', name='SetP', plot='T', plotwindow=1800),
        # ),
        BlockRow(
            Field(dev='T', plot='T', plotwindow=12*3600, width=100, height=40),
            Field(dev='Ts', plot='T', plotwindow=12*3600, width=100, height=40),
        ),
        ],
        setups='lakeshore',
    ),
    Block('Temperature (CCR18)', [
        BlockRow(
            Field(name='T_tube',dev='t_ccr18_tube'),
            Field(key='t_ccr18_tube/setpoint', name='Setpoint_tube'),
            Field(key='t_ccr18_tube/heaterpower',name='heaterpower_tube'),
        ),
        BlockRow(
            Field(dev='T', plot='T', plotwindow=12*3600, width=100, height=40),
            Field(key='t_ccr18_tube/setpoint', name='Setpoint', plot='T',
                  plotwindow=12*3600, width=100, height=40),
        ),
        ],
        setups='ccr18',
    ),
    Block('Temperature (CCR16)', [
        BlockRow(
            Field(name='T_stick',dev='t_ccr16_stick'),
            Field(key='t_ccr16_stick/setpoint', name='Setpoint_stick'),
            Field(key='t_ccr16_stick/heaterpower',name='heaterpower_stick'),
        ),
        BlockRow(
            Field(name='Pressure',dev='ccr16_p1'),
            Field(name='Coldhead',dev='T_ccr16_C'),
            Field(name='compressor',dev='ccr16_compressor'),
            Field(name='vacuum',dev='ccr16_vacuum_switch'),
        ),
        ],
        setups='ccr16',
    ),
)


devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'PUMA status monitor',
        filename='/pumacontrol/webroot/index.html',
        interval = 10,
        loglevel = 'info',
        cache = 'pumahw.puma.frm2.tum.de:14869',
        prefix = '/nicos',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 17,
        layout = [Row(_expcolumn),
                  Row(_leftcolumn, _middlecolumn, _rightcolumn)
                 ],
        noexpired = True,
    ),
)
