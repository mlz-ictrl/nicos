description = 'setup for the status monitor'
group = 'special'

expcolumn = [
    ('Experiment', [
        [{'key': 'exp/proposal', 'name': 'Proposal'},
         {'key': 'exp/title', 'name': 'Title', 'istext': True, 'width': 20},
         {'key': 'sample/samplename', 'name': 'Sample', 'istext': True, 'width': 15},
         {'name': 'Current status', 'key': 'exp/action', 'width': 55,
          'istext': True},
         {'key': 'filesink/lastfilenumber', 'name': 'Last file'}]
    ])]

filters = ('Filters', [
    ['Saph', 'Power', 'Shutter', 'ms1'],
    [{'dev': 'befilter', 'name': 'Be'}, {'dev': 'tbefilter', 'name': 'BeT'},
     {'dev': 'beofilter', 'name': 'BeO'}, {'dev': 'pgfilter', 'name': 'PG'}],
])

primary = ('Primary beam', [
    [{'dev': 'mono', 'name': 'ki_soll'}, {'key': 'mono/focmode', 'name': 'Focus'},
     {'dev': 'mth', 'name': 'mth (A1)'}, {'dev': 'mtt', 'name': 'mtt (A2)'}],
])

sample = ('Sample stage', [
    ['stx', 'sty', 'stz', 'atn'],
    ['sgx', 'sgy', {'dev': 'psi', 'name': 'psi (A3)'},
     {'dev': 'phi', 'name': 'phi (A4)'}],
])

analyzer = ('Analyzer', [
    [{'dev': 'ana', 'name': 'kf_soll'}, {'key': 'ana/focmode', 'name': 'Focus'},
     {'dev': 'ath', 'name': 'ath (A5)', 'unit': ''}, {'dev': 'att', 'name': 'att (A6)', 'unit': ''}],
])

column1 = [
#    filters,
    primary,
    sample,
    analyzer,
]

collimation = ('Collimation and Lengths', [
    ['ca1', 'ca2', 'ca3', 'ca4'],
    [{'dev': 'lsm', 'name': 'Src->Mono', 'unit': ''}, {'dev': 'lms', 'name': 'Mono->Samp', 'unit': ''},
     {'dev': 'lsa', 'name': 'Samp->Ana', 'unit': ''}, {'dev': 'lad', 'name': 'Samp->Det', 'unit': ''}],
])

detector = ('Detector', [
    ['timer', {'dev':'mon1', 'format':'%d'}, {'dev':'mon2', 'format':'%d'}],
    [{'dev':'det1', 'format': '%d'}, {'dev':'det2', 'format': '%d'},
     {'dev':'det3', 'format': '%d'}],
    [{'dev':'det4', 'format': '%d'}, {'dev':'det5', 'format': '%d'}],

])

lakeshore = ('LakeShore', [
    ['TA', 'TB'],
    [{'key': 't/setpoint', 'name': 'Setpoint'}, {'key': 't/p', 'name': 'P', 'width': 5},
     {'key': 't/i', 'name': 'I', 'width': 5}, {'key': 't/d', 'name': 'D', 'width': 5}],
])

column2 = [
#    collimation,
    detector,
    lakeshore,
]

devices = dict(
    Monitor = device('nicos.monitor.qt.Monitor',
                     title = 'PUMA status monitor',
                     loglevel = 'info',
                     cache = 'pumahw.puma.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     fontsize = 14,
                     valuefont = 'Luxi Mono',
                     layout = [[expcolumn], [column1, column2]],
                     notifiers = [],
                     warnings = [])
)
