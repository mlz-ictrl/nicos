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
cryodict = dict(cci3he1='3He-insert', cci3he2='3He-insert', cci3he3='3He-insert',
                ccidu1='Dilution-insert', ccidu2='Dilution-insert')
for cryo, name in cryodict.items():
    cryos.append(
        Block('%s %s' % (name, cryo.title()), [
            BlockRow(
                Field(dev='t_%s'   % cryo, name='Regulation', max=38),
                Field(dev='t_%s_a' % cryo, name='Sensor A', max=38),
                Field(dev='t_%s_b' % cryo, name='Sensor B',max=7),
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
        Block('%s-misc' % cryo.title(),[
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

# for setup magnet frm2-setup
magnet55 = Block('5.5T Magnet', [
    BlockRow(
        Field(dev='B_ccm55v'),
        Field(key='B_ccm55v/target', name='Target', fmtstr='%.2f'),
    ),
    ],
    setups='ccm55v',
)

# for setup magnet jcns jvm1
magnet5 = Block('5T Magnet', [
    BlockRow(
        Field(dev='I_vm5'),
        Field(key='I_vm5/target', name='Target', fmtstr='%.2f'),
    ),
    ],
    setups='jvm1',
)


magnet55supp = Block('Magnet', [
    BlockRow(
        Field(dev='sth_ccm55v',name='sth'),
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

magnet5supp = Block('Magnet', [
    BlockRow(
        Field(dev='T_vm5_sample', name='Ts'),
        Field(dev='T_vm5_vti', name='T'),
        Field(key='T_vm5_sample/setpoint',name='Setpoint',min=1,max=200),
        Field(key='T_vm5_sample/heater',name='Heater (%)'),
    ),
    BlockRow(
        Field(dev='vm5_lhe', name='He level'),
        Field(dev='T_vm5_magnet', name='T (coils)'),
        Field(dev='vm5_nv_manual', name='NV'),
    ),
    BlockRow(
        Field(dev='vm5_ppump', name='p(pump)'),
        Field(dev='vm5_psample', name='p(sample)'),
        Field(dev='vm5_pvti', name='p(vti)'),
    ),
    ],
    setups='jvm1',
)


vti = Block('VTI', [
#    BlockRow(
#        Field(dev='sTs'),
#        Field(dev='vti'),
#        Field(key='vti/setpoint',name='Setpoint',min=1,max=200),
#        Field(key='vti/heater',name='Heater (%)'),
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

magnet14t5 = Block('14.5T Magnet', [
    BlockRow(
        Field(dev='b15t', name='b15t', unit='T'),
        Field(key='b15t/target', name='Target', unit='T'),
        Field(key='b15t/ramp', name='Ramp', unit='T/min'),
    ),
    ],
    setups='15T',
)

kelvinox = Block('Kelvinox', [
    BlockRow(Field(dev='mc')),
    BlockRow(Field(key='mc/setpoint',name='Setpoint',unit='K')),
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

column2 = Column(collimation, detector) + Column(*cryos) + Column(*ccrs) + \
          Column(lakeshore, magnet55, magnet5, magnet14t5, vti)

column3 = Column(tas) + Column(magnet55supp, magnet5supp, kelvinox, foki,  memograph) + \
          Column(*cryosupps) + Column(*ccrsupps)

column4 = Column(lakeshoreplot) + Column(*cryoplots) + Column(*ccrplots)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
                     title = 'PANDA Status monitor',
                     filename = '/pandacontrol/webroot/index.html',
                     interval = 10,
                     loglevel = 'info',
                     cache = 'phys.panda.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 17,
                     layout = [[_expcolumn], [column1, column2, column3], [column4]]),
)
