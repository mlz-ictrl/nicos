description = 'setup for the HTML status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=15,
                       istext=True, maxlen=15),
                 Field(name='Sample',   key='sample/samplename', width=15,
                       istext=True, maxlen=15),
                 Field(name='Remark',   key='exp/remark',   width=30,
                       istext=True, maxlen=30),
                 Field(name='Current status', key='exp/action', width=30,
                       istext=True),
                 Field(name='Last file', key='exp/lastscan')),
        ],
    ),
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

column1 = Column(filters, primary, sample, analyzer)


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

lakeshore_hts = Block('LakeShore HTS', [
    BlockRow(
        Field(dev='t_ls_hts', name='Regul.'),
        Field(dev='t_ls_hts_a', name='Sensor A'),
        Field(dev='t_ls_hts_d', name='Sensor D'),
    ),
    BlockRow(
        Field(key='t_ls_hts/setpoint', name='Setpoint'),
        Field(key='t_ls_hts/p', name='P', width=5),
        Field(key='t_ls_hts/i', name='I', width=5),
        Field(key='t_ls_hts/d', name='D', width=5),
    ),
    ],
    setups='lakeshore_hts',
)

lakeshoreplot = Block('LakeShore', [
    BlockRow(
        Field(dev='T', plot='T',
            plotwindow=12*3600, width=100, height=40),
        Field(dev='Ts', plot='T',
            plotwindow=12*3600, width=100, height=40),
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
        Field(key='T_wm5v_sample/heater',name='Heater (%)'),
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


ccm12v = Block('12T Magnet', [
    BlockRow(
        Field(dev='B_ccm12v'),
        Field(key='B_ccm12v/target', name='Target', fmtstr='%.2f'),
    ),
    BlockRow(
        Field(dev='T_ccm12v_vti', name='VTI'),
        Field(dev='T_ccm12v_stick', name='Stick'),
    ),
    ],
    setups='ccm12v',
)

ccm12vplots = Block('12T Magnet', [
    BlockRow(
        Field(dev='T_ccm12v_vti', plot='Tccm12v',
            plotwindow=12*3600, width=30, height=20),
        Field(dev='T_ccm12v_stick', plot='Tccm12v',
            plotwindow=12*3600, width=30, height=20),
        ),
    ],
    setups='ccm12v',
)

foki = Block('Foki', [
    BlockRow(
        Field(dev='mfh'),
        Field(dev='mfv'),
    ),
    BlockRow(Field(dev='afh')),
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

tas = Block('TAS', [
        BlockRow(Field(name='H', key='panda/value[0]', format='%.3f', unit=''),
                 Field(name='K', key='panda/value[1]', format='%.3f', unit=''),
                 Field(name='L', key='panda/value[2]', format='%.3f', unit=''),
                 Field(name='E', key='panda/value[3]', format='%.3f', unit='')),
        BlockRow(Field(name='Mode', key='panda/scanmode'),
                 Field(name='ki', dev='mono'), Field(name='kf', dev='ana'),
                 Field(name='Unit', key='panda/energytransferunit')),
        ],
)

column2 = Column(collimation, detector, ccm12v) + Column(*cryos) + Column(*ccrs) + \
          Column(lakeshore, lakeshore_hts, ccm5v5, wm5v)

column3 = Column(tas) + Column(ccm5v5supp, wm5vsupp, foki, memograph) + \
          Column(*cryosupps)

column4 = Column(lakeshoreplot) + Column(*cryoplots) + Column(*ccrplots)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'PANDA Status monitor',
        filename = '/control/webroot/index.html',
        interval = 10,
        loglevel = 'info',
        cache = 'phys.panda.frm2',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 17,
        layout = [[_expcolumn],
                  [column1, column2, column3],
                  [column4]],
        noexpired = True,
    ),
)
