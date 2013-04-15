description = 'setup for the status monitor'
group = 'special'

_expcolumn = [
    ('Experiment', [
        [{'name': 'Proposal', 'key': 'exp/proposal', 'width': 7},
         {'name': 'Title', 'key': 'exp/title', 'width': 15,
          'istext': True, 'maxlen': 15},
         {'name': 'Sample', 'key': 'sample/samplename', 'width': 15,
          'istext': True, 'maxlen': 15},
         {'name': 'Remark', 'key': 'exp/remark', 'width': 30,
          'istext': True, 'maxlen': 30},
         {'name': 'Current status', 'key': 'exp/action', 'width': 30,
          'istext': True},
         {'name': 'Last file', 'key': 'filesink/lastfilenumber'}]]),
]

_column3 = [
    ('Analyzer', [[{'dev': 'ath'}, {'dev': 'att'}, {'dev': 'adr'}]],
     'analyzer'),
    ('Detector', [
        ['timer', 'mon1', 'mon2'],
        '---',
        ['ctr1',
         {'dev': 'MonHV', 'name': 'Mon HV', 'min': 490, 'width': 5},
         {'dev': 'DetHV', 'name': 'Det HV', 'min': 840, 'width': 5}],
        ],
     '!cascade'),
    ('Cascade', [
        [{'key': 'psd/lastcounts', 'name': 'ROI', 'item': 0, 'width': 9},
         {'key': 'psd/lastcounts', 'name': 'Total', 'item': 1, 'width': 9},
         {'key': 'psd/lastcontrast', 'name': 'MIEZE', 'item': 0, 'format': '%.3f', 'width': 6},
         {'key': 'psd/lastfilenumber', 'name': 'Last image'}],
        ['timer', 'mon1', 'mon2'],
        [{'dev': 'MonHV', 'name': 'Mon HV', 'min': 490, 'width': 5},
         {'dev': 'PSDGas', 'name': 'Gas', 'min': 'okay', 'width': 6},
         {'dev': 'PSDHV', 'name': 'HV', 'max': -2800, 'width': 5},
         {'dev': 'dtx', 'name': 'dtx'},
         ]
        ],
     'cascade'),
    ('3He cell', [
        [{'dev': 'pol', 'name': 'Polarization', 'width': 7},
         {'dev': 'He_GF', 'name': 'Guide field'}],
        ],
     'helios'),
    ('MIEZE', [
    #    [{'dev': 'mieze', 'item': 0, 'name': 'Setting', 'istext': True},
    #     {'dev': 'mieze', 'item': 1, 'name': 'Fourier time', 'unit': 'ps'},
    #     {'key': 'mieze/tuning', 'name': 'Tuning', 'istext': True}],
        ['freq1', 'amp1', 'coilamp1'],
        ['freq2', 'amp2', 'coilamp2'],
        ['fp1', 'fp2', {'dev': 'rp1', 'max': 20}, {'dev': 'rp2', 'max': 20}],
        ['dc1', 'dc2', 'freq3', {'dev': 'amp3', 'min': 4.999, 'max': 5.001}],
    ], 'mieze'),
#    ('X-Z table axes', [[{'dev': 'mx'}, {'dev': 'my'}]], 'gauss'),
    ('TAS', [
        [{'dev': 'mira', 'name': 'H', 'item': 0, 'format': '%.3f', 'unit': ' '},
         {'dev': 'mira', 'name': 'K', 'item': 1, 'format': '%.3f', 'unit': ' '},
         {'dev': 'mira', 'name': 'L', 'item': 2, 'format': '%.3f', 'unit': ' '},
         {'dev': 'mira', 'name': 'E', 'item': 3, 'format': '%.3f', 'unit': ' '}],
        [{'key': 'mira/scanmode', 'name': 'Mode'},
         {'dev': 'mono', 'name': 'ki'}, {'dev': 'ana', 'name': 'kf'},
         {'key': 'mira/energytransferunit', 'name': 'Unit'},],
    ], 'tas'),
    ('CCR 11', [
        [{'key': 't/setpoint', 'name': 'Setpoint', 'unitkey': 't/unit'},
         {'dev': 'Ts', 'name': 'Sample'}],
        [ dict(dev='T_ccr11_A', name='A'), dict(dev='T_ccr11_B', name='B'),
          dict(dev='T_ccr11_C', name='C'), dict(dev='T_ccr11_D', name='D')],
        [{'key': 't/p', 'name': 'P'}, {'key': 't/i', 'name': 'I'},
         {'key': 't/d', 'name': 'D'}, {'dev': 'ccr11_p1', 'name': 'p'}],
        ],
     'ccr11'),
    ('MIRA Magnet', [[{'dev': 'I', 'name': 'I'}]], 'miramagnet'),
    ('Temp. plot', [[{'dev': 'TA', 'plot': 'Temps', 'width': 40},
                     {'dev': 'TB', 'plot': 'Temps'},
                     {'dev': 'TC', 'plot': 'Temps'}]], 'ccr5'),
]

_column2 = [
    ('Slits', [[{'dev': 'ss1', 'name': 'Sample slit 1', 'width': 24, 'istext': True}],
               [{'dev': 'ss2', 'name': 'Sample slit 2', 'width': 24, 'istext': True}]],
     'slits'),
    ('Sample', [[{'dev': 'om'}, {'dev': 'srot'}, {'dev': 'phi'},],
                [{'dev': 'stx'}, {'dev': 'sty'}, {'dev': 'stz'}],
                [{'dev': 'sgx'}, {'dev': 'sgy'}]],
     'sample'),
    ('Sample environment', [
        [{'key': 't/setpoint', 'name': 'Setpoint', 'unitkey': 't/unit'},
         {'dev': 'T_ccr5_A', 'name': 'Sample'}, {'dev': 'T_ccr5_B', 'name': 'B'}, {'dev': 'T_ccr5_C', 'name': 'C'}],
        [{'key': 't/p', 'name': 'P'}, {'key': 't/i', 'name': 'I'},
         {'key': 't/d', 'name': 'D'}, {'dev': 'ccr5_p1', 'name': 'p'}],
        ],
     'ccr5'),
    ('FRM Magnet', [[{'dev': 'B'},
                    {'dev': 'm7T5_T1', 'max': 4.1}, {'dev': 'm7T5_T2', 'max': 4.1}],
                    [{'dev': 'm7T5_T3', 'max': 4.9}, {'dev': 'm7T5_T4', 'max': 4.5},
                     {'dev': 'm7T5_T8', 'max': 4.1}]], 'magnet75'),
    ('TTi', [['dct1', 'dct2'], ['dct3', 'dct4']], 'tti'),
    ('Relays', [['relay1', 'relay2']], 'relay'),
]

_column1 = [
    ('MIRA1', [[{'dev': 'FOL', 'name': 'FOL', 'width': 4},
                {'dev': 'flip1', 'name': 'Flip', 'width': 4}],
               ['mth', 'mtt'],
               ['mtx', 'mty'],
               ['mgx', {'dev': 'mchanger', 'name': 'mch'}],],
     'mono1'),
    ('MIRA2', [['m2th', 'm2tt'],
               ['m2tx', 'm2ty', 'm2gx'],
               ['m2fv', {'dev': 'atten1', 'name': 'Att1', 'width': 4},
                {'dev': 'atten2', 'name': 'Att2', 'width': 4},
                {'dev': 'flip2', 'name': 'Flip', 'width': 4}],
               [{'dev': 'lamfilter', 'name': 'Be', 'width': 4},
                {'dev': 'TBe', 'name': 'Be Temp', 'width': 6, 'max': 65},
                {'dev': 'PBe', 'name': 'Be P', 'width': 7, 'max': 1e-5, 'min': 1e-8}],
               [{'dev': 'ms2pos', 'name': 'Pos', 'width': 4, 'max': 'in'},
                {'dev': 'ms2', 'name': 'Mono slit 2', 'width': 20, 'istext': True}],
              ],
     'mono2'),
    ('Environment', [
        [{'dev': 'Power', 'name': 'Power', 'min': 19, 'format': '%.1f', 'width': 7},
         {'dev': 'Sixfold', 'name': '6-fold', 'min': 'open', 'width': 7},
         {'dev': 'NL6', 'name': 'NL6', 'min': 'open', 'width': 7}],
        [{'dev': 'Shutter', 'min': 'open', 'width': 7},
         {'dev': 'Cooling', 'max': 'okay', 'width': 7},
         {'dev': 'Crane', 'min': 10, 'width': 7}],
    ], 'reactor'),
]

_warnings = [
#    ('psdgas/value', '== "empty"', 'Change detector counting gas'),
#    ('TBe/value', '> 70', 'Check Be filter temperature'),
#    ('sixfold/value', '== "closed"', 'Six-fold shutter closed'),
]

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'MIRA Status monitor',
                     loglevel = 'info',
                     cache = 'mira1:14869',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 12,
                     padding = 5,
                     layout = [[_expcolumn], [_column1, _column2, _column3]])
)
