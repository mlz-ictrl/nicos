#  -*- coding: utf-8 -*-

name = 'setup for the status monitor'
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

_column1 = [
    ('Detector', [
        ['timer', 'mon1'],
        '---',
        [{'dev': 'MonHV', 'name': 'Mon HV', 'min': 490, 'width': 5},
         {'dev': 'DetHV', 'name': 'Det HV', 'min': 840, 'width': 5}],
        ],
     'detector'),
    ('Cascade', [
        [{'dev': 'psd', 'name': 'ROI', 'item': 0, 'width': 9},
         {'dev': 'psd', 'name': 'Total', 'item': 1, 'width': 9},
         {'key': 'psd/lastfilenumber', 'name': 'Last image'}],
        [{'dev': 'PSDGas', 'name': 'Gas', 'min': 'okay'},
         {'dev': 'PSDHV', 'name': 'HV', 'min': 2800, 'width': 5},
         {'dev': 'dtx', 'name': 'dtx'},
         ]
        ],
     'cascade'),
    ('MIEZE', [
        [{'dev': 'freq1', 'name': 'freq1'}, {'dev': 'freq2', 'name': 'freq2'}],
        [{'dev': 'amp1', 'name': 'amp1'},   {'dev': 'amp2', 'name': 'amp2'}],
        [{'dev': 'fp1', 'name': 'FP 1'},    {'dev': 'fp2', 'name': 'FP 2'}],
        [{'dev': 'rp1', 'name': 'RP 1'},    {'dev': 'rp2', 'name': 'RP 2'}],
        '---',
        [{'dev': 'dc1', 'name': 'DC 1'},    {'dev': 'dc2', 'name': 'DC 2'}],
        '---',
        [{'dev': 'freq3', 'name': 'freq3'}, {'dev': 'freq4', 'name': 'freq4'}],
        [{'dev': 'amp3', 'name': 'amp3'},   {'dev': 'amp4', 'name': 'amp4'}],
        [{'dev': 'Crane', 'min': 10, 'width': 7}],
    ], 'mieze'),
    ('X-Z table axes', [[{'dev': 'mx'}, {'dev': 'my'}]], 'gauss'),
]

_column2 = [
    ('Slits', [[{'dev': 's3', 'name': 'Slit 3', 'width': 24, 'istext': True}],
               [{'dev': 's4', 'name': 'Slit 4', 'width': 24, 'istext': True}]],
     'slits'),
    ('Sample', [[{'dev': 'om'}, {'dev': 'phi'}],
                [{'dev': 'stx'}, {'dev': 'sty'}, {'dev': 'stz'}],
                [{'dev': 'sgx'}, {'dev': 'sgy'}]],
     'sample'),
    ('Sample environment', [
        [{'key': 't/setpoint', 'name': 'Setpoint', 'unitkey': 't/unit'},
         {'dev': 'TA', 'name': 'Sample'}, 'TB', 'TC'],
        [{'key': 't/p', 'name': 'P'}, {'key': 't/i', 'name': 'I'},
         {'key': 't/d', 'name': 'D'}, {'dev': 'Pcryo', 'name': 'p'}],
        ],
     'lakeshore'),
    ('FRM Magnet', [[{'dev': 'B'}],
                    [{'dev': 'Tm1', 'max': 4.1}, {'dev': 'Tm2', 'max': 4.1},
                     {'dev': 'Tm3', 'max': 4.9}, {'dev': 'Tm4', 'max': 4.5}, 
                     {'dev': 'Tm8', 'max': 4.1}]], 'frm2magnet'),
    ('MIRA Magnet', [[{'dev': 'I', 'name': 'I'}]], 'miramagnet'),
]

_column3 = [
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
                {'dev': 'TBe', 'name': 'Be Temp', 'width': 6, 'max': 50},
                {'dev': 'PBe', 'name': 'Be P', 'width': 7, 'max': 1e-5}],
              ],
     'mono2'),
    ('Analyzer', [[{'dev': 'ath'}, {'dev': 'att'}]],
     'analyzer'),
    ('Reactor', [
        [{'dev': 'Power', 'name': 'Power', 'min': 19, 'format': '%d', 'width': 7},
         {'dev': 'Sixfold', 'name': '6-fold', 'min': 'open', 'width': 7},
         {'dev': 'NL6', 'name': 'NL6', 'min': 'open', 'width': 7}],
    ], 'reactor'),
]

_warnings = [
    ('psdgas/value', '== "empty"', 'Change detector counting gas'),
#    ('sixfold/value', '== "closed"', 'Six-fold shutter closed'),
#    ('freq3/value', '> 9', 'freq3 under frequency', 'mieze'),
#    ('freq4/value', '< 10', 'freq4 under frequency'),
]

devices = dict(
    Monitor = device('nicos.monitor.qt.Monitor',
                     title = 'MIRA Status monitor',
                     loglevel = 'debug',
                     server = 'mira1:14869',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 5,
                     layout = [[_expcolumn], [_column1, _column2, _column3]],
                     warnings = _warnings,
                     notifiers = [])
)
