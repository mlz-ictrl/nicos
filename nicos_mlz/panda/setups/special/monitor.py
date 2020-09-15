description = 'setup for the status monitor'

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
        Field(dev='saph', name='Saphir', istext=True),
        Field(dev='reactorpower', name='Power'),
        Field(dev='water', name='Water', istext=True),
        Field(dev='ms1', name='ms1'),
    ),
    BlockRow(
        Field(dev='befilter', name='Be', istext=True),
        Field(dev='tbefilter', name='BeT'),
        Field(dev='beofilter', name='BeO', istext=True),
        Field(dev='pgfilter', name='PG', istext=True),
    ),
    ],
)

primary = Block('Monochromator', [
    BlockRow(
        Field(dev='mono', name='Mono'),
        Field(key='mono/focmode', name='Focus', istext=True),
        Field(dev='mth', name='mth (A1)'),
        Field(dev='mtt', name='mtt (A2)'),
    ),
    ],
)

sample = Block('Sample stage', [
    BlockRow(
        Field(dev='stx', format='%.1f'),
        Field(dev='sty'),
        Field(dev='stz', format='%.2f'),
        Field(dev='sat'),
    ),
    BlockRow(
        Field(dev='sgx', format='%.2f'),
        Field(dev='sgy', format='%.2f'),
        Field(dev='sth', name='sth (A3)'),
        Field(dev='stt', name='stt (A4)'),
    ),
    ],
)

analyzer = Block('Analyzer', [
    BlockRow(
        Field(dev='ana', name='Ana'),
        Field(key='ana/focmode', name='Focus', istext=True),
        Field(dev='ath', name='ath (A5)', unit=''),
        Field(dev='att', name='att (A6)', unit=''),
    ),
    ],
)

collimation = Block('Collimation and Lengths', [
    BlockRow(
        Field(dev='ca1', default='None', width=5),
        Field(dev='ca2', default='None', width=5),
        Field(dev='ca3', default='None', width=5),
        Field(dev='ca4', default='None', width=5),
    ),
    BlockRow(
        Field(dev='lsm', width=5),
        Field(dev='lms', width=5),
        Field(dev='lsa', width=5),
        Field(dev='lad', width=5),
    ),
    BlockRow(
        Field(dev='ss1', width=25, istext=True),
    ),
    BlockRow(
        Field(dev='ss2', width=25, istext=True),
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
        Field(name='time', dev='timer'),
        Field(name='mon1', dev='mon1'),
        Field(name='mon2', dev='mon2'),
    ),
    BlockRow(
        Field(name='3.0meV', key='det/value[8]', format='%d'),
        Field(name='3.5meV', key='det/value[7]', format='%d'),
        Field(name='4.0meV', key='det/value[6]', format='%d'),
    ),
    BlockRow(
        Field(name='4.5meV', key='det/value[5]', format='%d'),
        Field(name='5.0meV', key='det/value[4]', format='%d'),
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

cam = Block('Camera', [
    BlockRow(
        Field(dev='camtimer'),
        Field(dev='cam_temp'),
    ),
    BlockRow(
        Field(key='exp/lastpoint', name='Last pict'),
    ),
    ],
    setups='camera',
)

# for setup lakeshore
lakeshore = Block('LakeShore', [
    BlockRow(
        Field(dev='t_ls340', name='Regul.'),
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
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=25, height=25, plotwindow=300,
              devices=['t_ls340/setpoint', 't_ls340_a', 't_ls340_b'],
              names=['Setpoint', 'A', 'B'],
        ),
    ),
    ],
    setups='lakeshore',
)


# generic Cryo-stuff
cryos = []
cryosupps = []
cryoplots = []
cryodict = dict(cci3he1='3He-insert', cci3he2='3He-insert', cci3he3='3He-insert',
                ccidu01='Dilution-insert', ccidu02='Dilution-insert')
for cryo, name in cryodict.items():
    cryos.append(
        Block('%s %s' % (name, cryo.title()), [
            BlockRow(
                Field(dev='t_%s'   % cryo, name='Regulation', max=38),
                Field(dev='t_%s_a' % cryo, name='Sensor A', max=38),
                Field(dev='t_%s_b' % cryo, name='Sensor B', max=7),
            ),
            BlockRow(
                Field(key='t_%s/setpoint' % cryo, name='Setpoint'),
                Field(key='t_%s/p' % cryo, name='P', width=7),
                Field(key='t_%s/i' % cryo, name='I', width=7),
                Field(key='t_%s/d' % cryo, name='D', width=7),
            ),
            ],
            setups=cryo,
        )
    )
    cryosupps.append(
        Block('%s-misc' % cryo.title(), [
            BlockRow(
                Field(dev='%s_p1' % cryo, name='Pump', width=10),
                Field(dev='%s_p4' % cryo, name='Cond.', width=10),
            ),
            BlockRow(
                Field(dev='%s_p5' % cryo, name='Dump', width=10),
                Field(dev='%s_p6' % cryo, name='IVC', width=10),
            ),
            BlockRow(
                Field(key='%s_flow' % cryo, name='Flow', width=10),
            ),
            ],
            setups=cryo,
        )
    )
    cryoplots.append(
        Block(cryo.title(), [
            BlockRow(
                Field(widget='nicos.guisupport.plots.TrendPlot',
                      plotwindow=300, width=25, height=25,
                      devices=['t_%s/setpoint' % cryo, 't_%s' % cryo],
                      names=['Setpoint', 'Regulation'],
                ),
            ),
            ],
            setups=cryo,
        )
    )


# generic CCR-stuff
ccrs = []
ccrsupps = []
ccrplots = []
for i in range(10, 22 + 1):
    ccrs.append(
        Block('CCR%d-Pulse tube' % i, [
            BlockRow(
                Field(dev='t_ccr%d_c' % i, name='Coldhead'),
                Field(dev='t_ccr%d_d' % i, name='Regulation'),
                Field(dev='t_ccr%d_b' % i, name='Sample'),
            ),
            BlockRow(
                Field(key='t_ccr%d/setpoint' % i, name='Setpoint'),
                Field(key='t_ccr%d/p' % i, name='P', width=7),
                Field(key='t_ccr%d/i' % i, name='I', width=7),
                Field(key='t_ccr%d/d' % i, name='D', width=6),
            ),
            ],
            setups='ccr%d and not cci3he*' % i,
        )
    )
    ccrsupps.append(
        Block('CCR%d' % i, [
            BlockRow(
                Field(dev='T_ccr%d_A' % i, name='A'),
                Field(dev='T_ccr%d_B' % i, name='B'),
            ),
            BlockRow(
                Field(dev='T_ccr%d_C' % i, name='C'),
                Field(dev='T_ccr%d_D' % i, name='D'),
            ),
            BlockRow(
                Field(dev='ccr%d_p1' % i, name='P1'),
                Field(dev='ccr%d_p2' % i, name='P2'),
            ),
            BlockRow(
                Field(key='t_ccr%d/setpoint' % i, name='SetP.', width=6),
                Field(key='t_ccr%d/p' % i, name='P', width=4),
                Field(key='t_ccr%d/i' % i, name='I', width=4),
                Field(key='t_ccr%d/d' % i, name='D', width=3),
            ),
            ],
            setups='ccr%d' % i,
        )
    )
    ccrplots.append(
        Block('CCR%d' % i, [
            BlockRow(
                Field(widget='nicos.guisupport.plots.TrendPlot',
                      plotwindow=300, width=25, height=25,
                      devices=['t_ccr%d/setpoint' % i, 't_ccr%d_c' % i,
                               't_ccr%d_d' % i, 't_ccr%d_b' % i],
                      names=['Setpoint', 'Coldhead', 'Regulation', 'Sample'],
                ),
            ),
            ],
            setups='ccr%d' % i,
        )
    )

miramagnet = Block('MIRA Magnet', [
    BlockRow(
        Field(dev='I'),
        Field(dev='B'),
    ),
    ],
    setups='miramagnet',
)

# for setup magnet frm2-setup
magnet55 = Block('5T Magnet', [
    BlockRow(
        Field(dev='B_ccm55v'),
        Field(key='B_ccm55v/target', name='Target', fmtstr='%.2f'),
    ),
    ],
    setups='ccm55v',
)

magnet55supp = Block('Magnet', [
    BlockRow(
        Field(dev='sth_ccm55v', name='sth'),
    ),
    # Maximum temperatures for field operation above 6.6 T (80A) taken from the
    # manual
    BlockRow(
        Field(dev='ccm55v_T1', max=4.3),
        Field(dev='ccm55v_T2', max=4.3),
    ),
    BlockRow(
        Field(dev='ccm55v_T3', max=5.1),
        Field(dev='ccm55v_T4', max=4.7),
    ),
    BlockRow(
        Field(dev='ccm55v_T5'),
        Field(dev='ccm55v_T6'),
    ),
    BlockRow(
        Field(dev='ccm55v_T7'),
        Field(dev='ccm55v_T8', max=4.3),
    ),
    ],
    setups='ccm55v',
)

# for setup magnet jcns
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
        Field(key='T_wm5v_sample/setpoint', name='Setpoint', min=1, max=200),
    ),
    BlockRow(
        Field(dev='wm5v_lhe', name='He level'),
        Field(dev='T_wm5v_magnet', name='T (coils)'),
        Field(dev='wm5v_nv_manual', name='NV'),
    ),
    BlockRow(
        Field(dev='wm5v_piso', name='p(iso)'),
        Field(dev='wm5v_psample', name='p(sa.)', fontsize = 12),
        Field(dev='wm5v_pvti', name='p(vti)'),
    ),
    ],
    setups='wm5v',
)

vti = Block('VTI', [
#    BlockRow(
#        Field(dev='sTs'),
#        Field(dev='vti'),
#        Field(key='vti/setpoint', name='Setpoint', min=1, max=200),
#        Field(key='vti/heater', name='Heater (%)'),
#    ),
    BlockRow(
        Field(dev='LHe'),
        Field(dev='LN2'),
    ),
    BlockRow(
        Field(dev='NV'),
        Field(dev='vti_pressure', name='p(UP)'),
        Field(dev='pressure_ls', name='p(DOWN)'),
        Field(key='vti_pressure/setpoint', name='setpoint'),
    ),
    ],
    setups='variox',
)

vtiplot = Block('Needle Valve', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=25, height=25, plotwindow=300,
              devices=['NV/setpoint', 'NV'],
              names=['Setpoint', 'Value'],
        ),
    ),
    ],
    setups='variox',
)

wm5vplots = Block('JVM 5', [
    BlockRow(
        Field(dev='wm5v_pvti', plot='p',
            plotwindow=3600, width=30, height=20),
        Field(dev='wm5v_nv_manual', plot='p',
            plotwindow=3600, width=30, height=20),
        ),
    BlockRow(
        Field(dev='T_wm5v_vti', plot='Tmag',
            plotwindow=12*3600, width=30, height=20),
        Field(dev='T_wm5v_sample', plot='Tmag',
            plotwindow=12*3600, width=30, height=20),
        ),
    BlockRow(
        Field(dev='wm5v_lhe', plot='lhe',
            plotwindow=12*3600, width=30, height=20),
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


kelvinox = Block('Kelvinox', [
    BlockRow(Field(dev='mc')),
    BlockRow(Field(key='mc/setpoint', name='Setpoint', unit='K')),
    BlockRow(Field(dev='sorb')),
    BlockRow(Field(dev='onekpot')),
    BlockRow(Field(dev='igh_p1')),
    BlockRow(Field(dev='igh_g1')),
    BlockRow(Field(dev='igh_g2')),
    ],
    setups='kelvinox',
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
        Field(dev='flow_in_panda', name='In'),
        Field(dev='flow_out_panda', name='Out'),
    ),
    BlockRow(
        Field(dev='t_in_panda', name='T In'),
        Field(dev='t_out_panda', name='T Out'),
    ),
    BlockRow(Field(dev='leak_panda', name='leak')),
    ],
)

column1 = Column(filters, primary, sample, analyzer) + Column(magnet55)
column2 = Column(collimation, detector, bambus, lakeshore_hts, ccm12v) + Column(*cryos) + Column(*ccrs) + \
          Column(lakeshore, miramagnet, wm5v, vti)

column3 = Column(magnet55supp, wm5vsupp, kelvinox, foki, memograph, cam) + \
          Column(*cryosupps) + Column(*ccrsupps)

column4 = Column(*cryoplots) + Column(*ccrplots) + \
          Column(wm5vplots) + Column(ccm12vplots) + Column(vtiplot) + \
          Column(lakeshoreplot)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'PANDA status monitor',
        loglevel = 'info',
        cache = 'phys.panda.frm2',
        prefix = 'nicos/',
        font = 'Liberation Sans',
        fontsize = 16,
        valuefont = 'Fira Code',
        layout = [Row(expcolumn),
                  Row(column1, column2, column3, column4)],
    )
)
