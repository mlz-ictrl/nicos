description = 'setup for the HTML status monitor'
group = 'special'

Row = Column = Block = BlockRow = lambda *args: args
Field = lambda *args, **kwds: args or kwds

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
    ]),
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
], '!always!')

primary = Block('Monochromator', [
    BlockRow(
        Field(dev='mono', name='Mono'),
        Field(key='mono/focmode', name='Focus'),
        Field(dev='mth', name='mth (A1)'),
        Field(dev='mtt', name='mtt (A2)'),
    ),
], '!always!')

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
], '!always!')

analyzer = Block('Analyzer', [
    BlockRow(
        Field(dev='ana', name='Ana'),
        Field(key='ana/focmode', name='Focus'),
        Field(dev='ath', name='ath (A5)', unit=''),
        Field(dev='att', name='att (A6)', unit=''),
    ),
], '!always!')

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
], '!always!')

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
], '!always!')

detector_small = Block('Detector', [
    BlockRow(
        Field(dev='timer'),
        Field(dev='mon1', format='%d'),
        Field(dev='mon2', format='%d'),
        Field(dev='det1', format='%d'),
        Field(dev='det2', format='%d'),
    ),
], '!always!')

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
],'lakeshore')

lakeshoreplot = Block('LakeShore', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=25, height=25, plotwindow=300,
              devices=['t_ls340/setpoint', 't_ls340_a', 't_ls340_b'],
              names=['Setpoint', 'A', 'B'],
        ),
    ),
], 'lakeshore')


# generic Cryo-stuff
cryos = []
cryosupps = []
cryoplots = []
cryonames = ['3He-insert', 'Dilution-insert', 'Dilution-insert', '3He-insert',
             '3He-insert'] # correct?
for i in range(1, 5 + 1):
    cryos.append(
        Block('Cryo%d:%s' % (i, cryonames[i-1]), [
            BlockRow(
                Field(dev='t_cryo%d' % i, name='Regulation', max=38),
                Field(dev='t_cryo%d_a' % i, name='Sensor A', max=38),
                Field(dev='t_cryo%d_b' % i, name='Sensor B',max=7),
            ),
            BlockRow(
                Field(key='t_cryo%d/setpoint' % i, name='Setpoint'),
                Field(key='t_cryo%d/p' % i, name='P', width=7),
                Field(key='t_cryo%d/i' % i, name='I', width=7),
                Field(key='t_cryo%d/d' % i, name='D', width=7),
            ),
        ],'cryo%d' % i)
    )
    cryosupps.append(
        Block('Cryo%d-misc' % i,[
            BlockRow(
                Field(dev='cryo%d_p1' % i, name='Pump', width=10),
                Field(dev='cryo%d_p4' % i, name='Cond.', width=10),
            ),
            BlockRow(
                Field(dev='cryo%d_p5' % i, name='Dump', width=10),
                Field(dev='cryo%d_p6' % i, name='IVC', width=10),
            ),
            BlockRow(
                Field(key='cryo%d_flow' % i, name='Flow', width=10),
            ),
        ],'cryo%d' % i)
    )
    cryoplots.append(
        Block('cryo%d' % i, [
            BlockRow(
                Field(widget='nicos.guisupport.plots.TrendPlot',
                      plotwindow=300, width=25, height=25,
                      devices=['t_cryo%d/setpoint' % i, 't_cryo%d' % i],
                      names=['Setpoint', 'Regulation'],
                ),
            ),
        ], 'cryo%d' % i)
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
        ],['ccr%d' % i, '!cryo*'])
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
        ], ['ccr%d' % i])
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
        ], 'ccr%d' % i)
    )

# for setup magnet frm2-setup
magnet75 = Block('7T Magnet', [
    BlockRow(
        Field(dev='B_m7T5'),
        Field(key='b_m7t5/target', name='Target', fmtstr='%.2f'),
    ),
],'magnet75')

magnet75supp = Block('Magnet', [
    BlockRow(
        Field(dev='sth_B7T5_Taco_motor',name='motor'),
        Field(dev='sth_B7T5_Taco_coder',name='coder'),
    ),
    BlockRow(
        Field(dev='m7T5_T1'),
        Field(dev='m7T5_T2'),
    ),
    BlockRow(
        Field(dev='m7T5_T3'),
        Field(dev='m7T5_T4'),
    ),
    BlockRow(
        Field(dev='m7T5_T5'),
        Field(dev='m7T5_T6'),
    ),
    BlockRow(
        Field(dev='m7T5_T7'),
        Field(dev='m7T5_T8'),
    ),
],'magnet75')

# for setup magnet PANDA-setup
magnet7t5 = Block('7T Magnet', [
    BlockRow(
        Field(dev='B_m7T5'),
        Field(key='b_m7t5/target', name='Target', fmtstr='%.2f'),
    ),
],'7T5')

magnet7t5supp = Block('Magnet', [
    BlockRow(
        Field(dev='sth_B7T5_Taco_motor',name='motor'),
        Field(dev='sth_B7T5_Taco_coder',name='coder'),
    ),
    # Maximum temeratures for field operation above 80A (6.6T) taken from the manual
    BlockRow(
        Field(dev='m7T5_T1',max=4.3),
        Field(dev='m7T5_T2',max=4.3),
    ),
    BlockRow(
        Field(dev='m7T5_T3',max=5.1),
        Field(dev='m7T5_T4',max=4.7),
    ),
    BlockRow(
        Field(dev='m7T5_T5'),
        Field(dev='m7T5_T6'),
    ),
    BlockRow(
        Field(dev='m7T5_T7'),
        Field(dev='m7T5_T8',max=4.3),
    ),
],'7T5')

vti = Block('VTI', [
    BlockRow(
        Field(dev='sTs'),
        Field(dev='vti'),
        Field(key='vti/setpoint',name='Setpoint',min=1,max=200),
        Field(key='vti/heater',name='Heater (%)'),
    ),
    BlockRow(
        Field(dev='NV'),
        Field(dev='LHe'),
        Field(dev='LN2'),
    ),
],['15T', 'variox'])

magnet14t5 = Block('14.5T Magnet', [
    BlockRow(
        Field(dev='b15t', name='b15t', unit='T'),
        Field(key='b15t/target', name='Target', unit='T'),
        Field(key='b15t/ramp', name='Ramp', unit='T/min'),
    ),
],'15T')

kelvinox = Block('Kelvinox', [
    BlockRow(Field(dev='mc')),
    BlockRow(Field(key='mc/setpoint',name='Setpoint',unit='K')),
    BlockRow(Field(dev='sorb')),
    BlockRow(Field(dev='onekpot')),
    BlockRow(Field(dev='igh_p1')),
    BlockRow(Field(dev='igh_g1')),
    BlockRow(Field(dev='igh_g2')),
],'kelvinox')

foki = Block('Foki', [
    BlockRow(
        Field(dev='mfh'),
        Field(dev='mfv'),
    ),
    BlockRow(Field(dev='afh')),
], '!always!')

column2 = Column(collimation, detector) + Column(*cryos) + Column(*ccrs) + \
          Column(lakeshore, magnet75, magnet7t5, magnet14t5, vti)

column3 = Column(magnet75supp, magnet7t5supp, kelvinox, foki) + \
          Column(*cryosupps) + Column(*ccrsupps)

column4 = Column(lakeshoreplot) + Column(*cryoplots) + Column(*ccrplots)

devices = dict(
    Monitor = device('services.monitor.html.Monitor',
                     title = 'PANDA Status monitor',
                     filename = '/data/pandastatus/index.html',
                     interval = 10,
                     loglevel = 'info',
                     cache = 'phys.panda.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 17,
                     layout = [[_expcolumn], [column1, column2, column3], [column4]]),
)
