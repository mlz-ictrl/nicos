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

_column1 = [
    ('Detector', [
        ['timer', 'mon1', 'mon2'],
        '---',
        ['ctr1',
         {'dev': 'MonHV', 'name': 'Mon HV', 'min': 490, 'width': 5},
         {'dev': 'DetHV', 'name': 'Det HV', 'min': 840, 'width': 5}],
        ],
     'detector'),
    ('Cascade', [
        [{'key': 'psd/lastcounts', 'name': 'ROI', 'item': 0, 'width': 9},
         {'key': 'psd/lastcounts', 'name': 'Total', 'item': 1, 'width': 9},
         {'key': 'psd/lastfilenumber', 'name': 'Last image'}],
        [{'dev': 'PSDGas', 'name': 'Gas', 'min': 'okay'},
         {'dev': 'PSDHV', 'name': 'HV', 'max': -2800, 'width': 6},
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
#    ('X-Z table axes', [[{'dev': 'mx'}, {'dev': 'my'}]], 'gauss'),
    ('TAS', [
        [{'dev': 'mira', 'name': 'H', 'item': 0, 'format': '%.3f', 'unit': ' '}, {'dev': 'mira', 'name': 'K', 'item': 1, 'format': '%.3f', 'unit': ' '},
         {'dev': 'mira', 'name': 'L', 'item': 2, 'format': '%.3f', 'unit': ' '}, {'dev': 'mira', 'name': 'E', 'item': 3, 'format': '%.3f', 'unit': ' '}],
        [{'key': 'mira/scanmode', 'name': 'Mode'},
         {'dev': 'mono', 'name': 'ki'}, {'dev': 'ana', 'name': 'kf'}, {'key': 'mira/energytransferunit', 'name': 'Unit'},],
    ], 'tas'),
    ('MIRA Magnet', [[{'dev': 'I', 'name': 'I'}]], 'miramagnet'),
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
         {'dev': 'TA', 'name': 'Sample'}, 'TB', 'TC'],
        [{'key': 't/p', 'name': 'P'}, {'key': 't/i', 'name': 'I'},
         {'key': 't/d', 'name': 'D'}, {'dev': 'Pcryo', 'name': 'p'}],
        ],
     'lakeshore'),
    ('FRM Magnet', [[{'dev': 'B'}],
                    [{'dev': 'Tm1', 'max': 4.1}, {'dev': 'Tm2', 'max': 4.1},
                     {'dev': 'Tm3', 'max': 4.9}, {'dev': 'Tm4', 'max': 4.5}, 
                     {'dev': 'Tm8', 'max': 4.1}]], 'frm2magnet'),
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
                {'dev': 'TBe', 'name': 'Be Temp', 'width': 6, 'max': 65},
                {'dev': 'PBe', 'name': 'Be P', 'width': 7, 'max': 1e-5}],
               [{'dev': 'slit0', 'name': 'Mono slit 2'}],
              ],
     'mono2'),
    ('Analyzer', [[{'dev': 'ath'}, {'dev': 'att'}, {'dev': 'adr'}]],
     'analyzer'),
    ('Reactor', [
        [{'dev': 'Power', 'name': 'Power', 'min': 19, 'format': '%d', 'width': 7},
         {'dev': 'Sixfold', 'name': '6-fold', 'min': 'open', 'width': 7},
         {'dev': 'NL6', 'name': 'NL6', 'min': 'open', 'width': 7}],
    ], 'reactor'),
]

_warnings = [
    ('psdgas/value', '== "empty"', 'Change detector counting gas'),
    ('TBe/value', '> 70', 'Check Be filter temperature'),
    ('sixfold/value', '== "closed"', 'Six-fold shutter closed'),
#    ('freq3/value', '> 9', 'freq3 under frequency', 'mieze'),
#    ('freq4/value', '< 10', 'freq4 under frequency'),
]

devices = dict(
    email    = device('nicos.notify.Mailer',
                      sender = 'nicos@mira1',
                      receivers = ['rgeorgii@frm2.tum.de'],
                      subject = 'MIRA'),

    smser    = device('nicos.notify.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = ['01719251564']),

    Monitor = device('nicos.monitor.qt.Monitor',
                     title = 'MIRA Status monitor',
                     loglevel = 'debug',
                     cache = 'mira1:14869',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 5,
                     layout = [[_expcolumn], [_column1, _column2, _column3]],
                     warnings = _warnings,
                     notifiers = ['smser', 'email'])
)
