description = 'setup for the status monitor in Petrs office'

group = 'special'

expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(key='exp/proposal', name='Proposal'),
            Field(key='exp/title', name='Title', istext=True, width=70),
            Field(key='sample/samplename', name='Sample', istext=True, width=30),
        ),
        BlockRow(
            Field(key='exp/action', name='Current status', width=100,
                  istext=True, default='Idle' ),
            Field(key='exp/lastscan', name='Last file'),
        ),
        ],
    )
)

filters = Block('Primary Beam/Filters', [
    BlockRow(
        Field(dev='saph', name='Saphir'),
        Field(dev='reactorpower', name='Power'),
        Field(dev='water', name='Water'),
        Field(dev='ms1', name='ms1'),
    ),
    BlockRow(
        Field(dev='befilter', name='Be'),
        Field(dev='tbefilter', name='BeT'),
        Field(dev='beofilter', name='BeO'),
        Field(dev='pgfilter', name='PG'),
    ),
    ],
)

primary = Block('Monochromator', [
    BlockRow(
        Field(dev='mono', name='Mono'),
        Field(key='mono/focmode', name='Focus'),
        Field(dev='mth', name='mth (A1)'),
        Field(dev='mtt', name='mtt (A2)'),
    ),
    ],
)

sample = Block('Sample stage', [
    BlockRow(
        Field(dev='stx', format='%.1f'),
        Field(dev='sty'),
        Field(dev='stz',format='%.2f'),
        Field(dev='sat'),
    ),
    BlockRow(
        Field(dev='sgx',format='%.2f'),
        Field(dev='sgy',format='%.2f'),
        Field(dev='sth', name='sth (A3)'),
        Field(dev='stt', name='stt (A4)'),
    ),
    ],
)

analyzer = Block('Analyzer', [
    BlockRow(
        Field(dev='ana', name='Ana'),
        Field(key='ana/focmode', name='Focus'),
        Field(dev='ath', name='ath (A5)', unit=''),
        Field(dev='att', name='att (A6)', unit=''),
    ),
    ],
)

collimation = Block('Collimation and Lengths', [
    BlockRow(
        Field(dev='ca1',default='None'),
        Field(dev='ca2',default='None'),
        Field(dev='ca3',default='None'),
        Field(dev='ca4',default='None'),
    ),
    BlockRow(
        Field(dev='lsm'),
        Field(dev='lms'),
        Field(dev='lsa'),
        Field(dev='lad'),
    ),
    ],
)


detector = Block('Detector', [
    BlockRow(
        Field(dev='timer'),
        Field(dev='mon1', format='%d'),
        Field(dev='mon2', format='%d'),
    ),
    BlockRow(
        Field(dev='det1', format='%d'),
        Field(dev='det2', format='%d'),
    ),
    ],
    setups='panda',
)

bambus = Block('Detector', [
    BlockRow(
        Field(name='events', key='det/value[0]', format='%d'),
        Field(name='time', key='det/value[1]', format='%4g'),
        Field(name='mon1', key='det/value[2]', format='%d'),
        Field(name='mon2', key='det/value[3]', format='%d'),
        Field(name='ch_sum', key='det/value[4]', format='%d'),
    ),
    BlockRow(
        Field(name='2.5 A1', key='det/value[5]', format='%d'),
        Field(name='3.0 A3', key='det/value[7]', format='%d'),
        Field(name='3.5 A5', key='det/value[9]', format='%d'),
        Field(name='4.0 A7', key='det/value[11]', format='%d'),
        Field(name='4.5 A9', key='det/value[13]', format='%d'),
    ),
    BlockRow(
        Field(name='2.5 B2', key='det/value[6]', format='%d'),
        Field(name='3.0 B4', key='det/value[8]', format='%d'),
        Field(name='3.5 B6', key='det/value[10]', format='%d'),
        Field(name='4.0 B8', key='det/value[12]', format='%d'),
        Field(name='4.5 B10', key='det/value[14]', format='%d'),
    ),
    ],
    setups='bambus',
)

detector_small = Block('Detector', [
    BlockRow(
        Field(dev='timer'),
        Field(dev='mon1', format='%d'),
        Field(dev='mon2', format='%d'),
        Field(dev='det1', format='%d'),
        Field(dev='det2', format='%d'),
    ),
    ],
)

# for setup lakeshore
lakeshore = Block('LakeShore', [
    BlockRow(
        Field(dev='t_ls340', name='Regulation'),
        Field(dev='t_ls340_a', name='Sensor A'),
        Field(dev='t_ls340_b', name='Sensor B'),
    ),
    BlockRow(
        Field(key='t_ls340/setpoint', name='Setpoint'),
        Field(key='t_ls340/p', name='P', width=5),
        Field(key='t_ls340/i', name='I', width=5),
        Field(key='t_ls340/d', name='D', width=5),
    ),
    ],
    setups='lakeshore',
)

lakeshoreplot = Block('LakeShore', [
    BlockRow(
        Field(dev='T', plot='T',
            plotwindow=12*3600, width=45, height=30),
        Field(dev='Ts', plot='T',
            plotwindow=12*3600, width=45, height=30),
        ),
    ],
    setups='lakeshore',
)


# generic Cryo-stuff
cryos = []
cryosupps = []
cryoplots = []
cryonames = ['cci3he01', 'cci3he02', 'cci3he03', 'cci3he10', 'cci3he11',
             'cci3he12', 'ccidu01', 'ccidu02']
for cryo in cryonames:
    cryos.append(SetupBlock(cryo))
    cryosupps.append(SetupBlock(cryo, 'pressures'))
    cryoplots.append(SetupBlock(cryo, 'plots'))


# generic CCR-stuff
ccrs = []
ccrplots = []
for i in range(10, 25 + 1):
    if i == 13:
        continue
    ccrs.append(SetupBlock(f'ccr{i}'))
    ccrplots.append(SetupBlock(f'ccr{i}', 'plots'))

miramagnet = Block('MIRA Magnet', [
    BlockRow(
        Field(dev='I_miramagnet'),
        Field(dev='B_miramagnet'),
    ),
    ],
    setups='miramagnet',
)

# for setup magnet frm2-setup
ccm5v5 = SetupBlock('ccm5v5')
ccm5v5supp = SetupBlock('ccm5v5', 'temperatures')

# for setup magnet jcns 5T
wm5v = Block('5T Magnet', [
    BlockRow(
        Field(dev='I_wm5v'),
        Field(key='I_wm5v/target', name='Target', fmtstr='%.2f'),
    ),
    ],
    setups='wm5v',
)
wm5vsupp = Block('Magnet', [
    BlockRow(
        Field(dev='T_wm5v_sample', name='Ts'),
        Field(dev='T_wm5v_vti', name='T'),
        Field(key='T_wm5v_sample/setpoint',name='Setpoint',min=1,max=200),
        Field(key='T_wm5v_sample/heateroutput',name='Heater'),
    ),
    BlockRow(
        Field(dev='wm5v_lhe', name='He level'),
        Field(dev='T_wm5v_magnet', name='T (coils)'),
        Field(dev='wm5v_nv_manual', name='NV'),
    ),
    BlockRow(
        Field(dev='wm5v_piso', name='p(iso)'),
        Field(dev='wm5v_psample', name='p(sample)'),
        Field(dev='wm5v_pvti', name='p(vti)'),
    ),
    ],
    setups='wm5v',
)

wm5vplots = Block('JVM 5', [
    BlockRow(
        Field(dev='wm5v_pvti', plot='p',
            plotwindow=3600, width=45, height=25),
        Field(dev='wm5v_nv_manual', plot='p',
            plotwindow=3600, width=45, height=25),
        ),
    BlockRow(
        Field(dev='T_wm5v_vti', plot='Tmag',
            plotwindow=12*3600, width=45, height=25),
        Field(dev='T_wm5v_sample', plot='Tmag',
            plotwindow=12*3600, width=45, height=25),
        ),
    BlockRow(
        Field(dev='wm5v_lhe', plot='lhe',
            plotwindow=12*3600, width=45, height=20),
        ),
    ],
    setups='wm5v',
)

foki = Block('Foki', [
    BlockRow(
        Field(dev='mfh'),
        Field(dev='mfv'),
        Field(dev='afh')),
    ],
)

memograph = Block('Water Flow', [
    BlockRow(
        Field(dev='cooling_flow_in', name='In'),
        Field(dev='cooling_flow_out', name='Out'),
    ),
    BlockRow(
        Field(dev='cooling_t_in', name='T In'),
        Field(dev='cooling_t_out', name='T Out'),
    ),
    BlockRow(Field(dev='cooling_leak', name='leak')),
    ],
)

column1 = Column(filters, primary, sample, analyzer) + \
          Column(ccm5v5supp, wm5vsupp)

column2 = Column(detector, bambus) + Column(*cryos) + Column(*ccrs) + \
          Column(lakeshore, miramagnet, wm5v, ccm5v5) + \
          Column(foki, memograph)

column3 = Column(*cryosupps) + Column(wm5vplots) + \
          Column(*cryoplots) + Column(*ccrplots) + Column(lakeshoreplot)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'PANDA office status monitor',
        loglevel = 'info',
        cache = 'phys.panda.frm2',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        fontsize = 14,
        valuefont = 'Luxi Sans',
        layout = [Row(expcolumn),
                  Row(column1, column2, column3)],
    )
)
