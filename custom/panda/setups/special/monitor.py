description = 'setup for the status monitor'

group = 'special'

expcolumn = [
    ('Experiment', [
        [{'key': 'exp/proposal', 'name': 'Proposal'},
         {'key': 'exp/title', 'name': 'Title', 'istext': True, 'width': 70},
         {'key': 'sample/samplename', 'name': 'Sample', 'istext': True, 'width': 30},],[
         {'name': 'Current status', 'key': 'exp/action', 'width': 100,
          'istext': True, 'default':'Idle' },
         {'key': 'exp/lastscan', 'name': 'Last file'}]
    ])]

filters = ('Primary Beam/Filters', [
    ['Saph', 'Power', 'Shutter', 'ms1'],
    [{'dev': 'befilter', 'name': 'Be'}, dict(dev='tbefilter', name= 'BeT'),
     {'dev': 'beofilter', 'name': 'BeO'}, {'dev': 'pgfilter', 'name': 'PG'}],
])

primary = ('Monochromator', [
    [{'dev': 'mono', 'name': 'Mono'}, {'key': 'mono/focmode', 'name': 'Focus'},
     {'dev': 'mth', 'name': 'mth (A1)'}, {'dev': 'mtt', 'name': 'mtt (A2)'}],
])

sample = ('Sample stage', [
    [{'dev':'stx','format':'%.1f'}, 'sty', dict(dev='stz',format='%.2f'), 'sat'],
    [dict(dev='sgx',format='%.2f'), dict(dev='sgy',format='%.2f'), {'dev': 'sth', 'name': 'sth (A3)'},
     {'dev': 'stt', 'name': 'stt (A4)'}],
])

analyzer = ('Analyzer', [
    [{'dev': 'ana', 'name': 'Ana'}, {'key': 'ana/focmode', 'name': 'Focus'},
     {'dev': 'ath', 'name': 'ath (A5)', 'unit': ''}, {'dev': 'att', 'name': 'att (A6)', 'unit': ''}],
])

collimation = ('Collimation and Lengths', [
    [dict(dev='ca1',default='None'), 'ca2', 'ca3', 'ca4'],
    ['lsm','lms','lsa','lad'],
#    [dict(dev='lsm', name='Src->Mono',width=8),
#     dict(dev='lms', name='Mono->Samp',width=8),],
#    [dict(dev='lsa', name='Samp->Ana',width=8),
#     dict(dev='lad', name='Ana->Det',width=8)],
])

column1 = [filters, primary, sample, analyzer]

detector = ('Detector', [
    ['timer', {'dev':'mon1', 'format':'%d'}, {'dev':'mon2', 'format':'%d'}],
    [{'dev':'det1', 'format': '%d'}, {'dev':'det2', 'format': '%d'}],
])

detector_small = ('Detector', [
    ['timer', {'dev':'mon1', 'format':'%d'}, {'dev':'mon2', 'format':'%d'},
    {'dev':'det1', 'format': '%d'}, {'dev':'det2', 'format': '%d'}],
])

# for setup lakeshore
lakeshore = ('LakeShore', [
    ['T_ls340', 'T_ls340_A','T_ls340_B'],
    [{'dev': 't_ls340/setpoint', 'name': 'Setpoint'}, {'dev': 't_ls340/p', 'name': 'P', 'width': 5},
     {'dev': 't_ls340/i', 'name': 'I', 'width': 5}, {'dev': 't_ls340/d', 'name': 'D', 'width': 5}],
],'lakeshore')

# for setup cryo1
cryo1 = ('Cryo1:3He-insert', [
    [   dict( key='t_cryo1/value', name='Regulation', max=38),
        dict( key='t_cryo1_a/value', name='Sensor A', max=38),
        dict( key='t_cryo1_b/value', name='Sensor B',max=7),
    ],[
        dict( key='t_cryo1/setpoint', name='Setpoint'),
        dict( key='t_cryo1/p', name='P', width=7),
        dict( key='t_cryo1/i', name='I', width=7),
        dict( key='t_cryo1/d', name='D', width=7),
    ],
],'cryo1')

cryo1supp = ('Cryo1-misc',[
    [   dict( key='cryo1_p1/value', name='Pump (mbar)', width=10),
        dict( key='cryo1_p4/value', name='Cond. (bar)', width=10),
    ],[
        dict( key='cryo1_p5/value', name='Dump (bar)', width=10),
        dict( key='cryo1_p6/value', name='IVC (mbar)', width=10),
    ],[
        dict( key='cryo1_flow/value', name='Flow', width=10),
    ]
],'cryo1')

# for setup cryo3
cryo3 = ('Cryo3:dilution-insert', [
    [   dict( key='t_cryo3/value', name='Regulation', max=38),
        dict( key='t_cryo3_a/value', name='Sensor A', max=38),
        dict( key='t_cryo3_b/value', name='Sensor B',max=7),
    ],[
        dict( key='t_cryo3/setpoint', name='Setpoint'),
        dict( key='t_cryo3/p', name='P', width=7),
        dict( key='t_cryo3/i', name='I', width=7),
        dict( key='t_cryo3/d', name='D', width=7),
    ],
],'cryo3')

cryo3supp = ('Cryo3-misc',[
    [   dict( key='cryo3_p1/value', name='Pump (mbar)', width=10),
        dict( key='cryo3_p4/value', name='Cond. (bar)', width=10),
    ],[
        dict( key='cryo3_p5/value', name='Dump (bar)', width=10),
        dict( key='cryo3_p6/value', name='IVC (mbar)', width=10),
    ],[
        dict( key='cryo3_flow/value', name='Flow', width=10),
    ]
],'cryo3')

# for setup cryo4
cryo4 = ('Cryo4:3He-insert', [
    [   dict( key='t_cryo4/value', name='Regulation'),
        dict( key='t_cryo4_a/value', name='Sensor A'),
        dict( key='t_cryo4_b/value', name='Sensor B'),
    ],
],'cryo4')

cryo4supp = ('Cryo4-misc',[
    [   dict( key='cryo4_p1/value', name='Pump (mbar)', width=10),
        dict( key='cryo4_p4/value', name='Cond. (bar)', width=10),
    ],[
        dict( key='cryo4_p5/value', name='Dump (bar)', width=10),
        dict( key='cryo4_p6/value', name='IVC (mbar)', width=10),
    ],[
        dict( key='cryo4_flow/value', name='Flow', width=10),
    ]
],'cryo4')

# for setup cryo5
cryo5 = ('Cryo5:3He-insert', [
    [   dict( key='t_cryo5/value', name='Regulation'),
        dict( key='t_cryo5_a/value', name='Sensor A'),
        dict( key='t_cryo5_b/value', name='Sensor B'),
    ],
],'cryo5')

cryo5supp = ('Cryo5-misc',[
    [   dict( key='cryo5_p1/value', name='Pump (mbar)', width=10),
        dict( key='cryo5_p4/value', name='Cond. (bar)', width=10),
    ],[
        dict( key='cryo5_p5/value', name='Dump (bar)', width=10),
        dict( key='cryo5_p6/value', name='IVC (mbar)', width=10),
    ],[
        dict( key='cryo5_flow/value', name='Flow', width=10),
    ]
],'cryo5')


# for setup ccr11
ccr11 = ('CCR11-Pulse tube', [
    [dict(key='t_ccr11_a/value',name='Cooling'),
    dict(key='t_ccr11/value',name='Regulation'),
    dict(key='t_ccr11_b/value',name='Sample'),],
    [{'key': 't_ccr11/setpoint', 'name': 'Setpoint'}, {'key': 't_ccr11/p', 'name': 'P', 'width': 7},
     {'key': 't_ccr11/i', 'name': 'I', 'width': 7}, {'key': 't_ccr11/d', 'name': 'D', 'width': 6, }],
],'ccr11')

ccr11supp = ( 'CCR11', [
    ['T_ccr11_A','T_ccr11_B'],
    ['T_ccr11_C','T_ccr11_D'],
    ['ccr11_p1','ccr11_p2'],
], 'ccr11')

# for setup magnet frm2-setup
magnet75 = ('7T Magnet', [
    [ 'B_m7T5', dict(key='b_m7t5/target', name='Target', fmtstr='%.2f'),
    ],
],'magnet75')

magnet75supp = ('Magnet', [
    [dict(dev='sth_B7T5_Taco_motor',name='motor'),
    dict(dev='sth_B7T5_Taco_coder',name='coder')],
    [dict(dev='m7T5_T1'),
    dict(dev='m7T5_T2')],
    [dict(dev='m7T5_T3'),
    dict(dev='m7T5_T4')],
    [dict(dev='m7T5_T5'),
    dict(dev='m7T5_T6')],
    [dict(dev='m7T5_T7'),
    dict(dev='m7T5_T8')],
],'magnet75')

# for setup magnet PANDA-setup
magnet7t5 = ('7T Magnet', [
    [ 'B_m7T5', dict(key='b_m7t5/target', name='Target', fmtstr='%.2f'),
    ],
],'7T5')

magnet7t5supp = ('Magnet', [
    [dict(dev='sth_B7T5_Taco_motor',name='motor'),
    dict(dev='sth_B7T5_Taco_coder',name='coder')],
    [dict(dev='m7T5_T1',max=4.3),       # Maximum temeratures for field operation above  80A (6.6T) taken from the manual
    dict(dev='m7T5_T2',max=4.3)],
    [dict(dev='m7T5_T3',max=5.1),
    dict(dev='m7T5_T4',max=4.7)],
    [dict(dev='m7T5_T5'),
    dict(dev='m7T5_T6')],
    [dict(dev='m7T5_T7'),
    dict(dev='m7T5_T8',max=4.3)],
],'7T5')

vti = ('VTI', [
    ['sTs','vti',dict(key='vti/setpoint',name='Setpoint',min=1,max=200),
        dict(key='vti/heater',name='Heater (%)'),],
    ['NV','LHe','LN2'],
    ],'15T')

variox = ('VTI', [
    ['sTs','vti',dict(key='vti/setpoint',name='Setpoint',min=1,max=200),
        dict(key='vti/heater',name='Heater (%)'),],
    ['NV','LHe','LN2'],
    ],'variox')

magnet14t5 = ('14.5T Magnet', [
    [   dict(key='b15t/value',name='b15t',unit='T'),
        dict(key='b15t/target',name='Target',unit='T'),
        dict(key='b15t/ramp',name='Ramp', unit='T/min')],
],'15T')

kelvinox = ('Kelvinox', [
    [   'mc' ],
    [ dict(key='mc/setpoint',name='Setpoint',unit='K')],
    [ 'sorb' ],
    [ 'onekpot'],
    [   'igh_p1' ],
    [ 'igh_g1'],
    ['igh_g2'],
],'kelvinox')

foki = ('Foki', [
  ['mfh','mfv'],
  ['afh'],
])

column2 = [collimation, detector, cryo1, cryo3, cryo4, cryo5, lakeshore, magnet75, magnet7t5, magnet14t5, vti, variox ]

column3 = [cryo1supp, cryo3supp, cryo4supp, cryo5supp, ccr11]

column4 = [magnet75supp, magnet7t5supp, kelvinox, foki]

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'PANDA status monitor',
                     loglevel = 'info',
                     cache = 'pandasrv.panda.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     fontsize = 17,
                     valuefont = 'Luxi Sans',
                     layout = [[expcolumn], [column1, column2, column3, column4]],
                     )
)
