description = 'setup for the status monitor'
group = 'special'

expcolumn = [
    ('Experiment', [
        [{'key': 'exp/proposal', 'name': 'Proposal'},
         {'key': 'exp/title', 'name': 'Title', 'istext': True, 'width': 40},
         {'name': 'Current status', 'key': 'exp/action', 'width': 30,
          'istext': True},
         {'key': 'filesink/lastfilenumber', 'name': 'Last file number'}]
    ])]

filters = ('Filters', [
    ['Saph', 'Power', 'Shutter', 'ms1'],
    [{'dev': 'befilter', 'name': 'Be'}, {'dev': 'befiltertemp', 'name': 'BeT'},
     {'dev': 'beofilter', 'name': 'BeO'}, {'dev': 'pgfilter', 'name': 'PG'}],
])

primary = ('Primary beam', [
    [{'dev': 'mono', 'name': 'ki_soll'}, {'key': 'mono/focmode', 'name': 'Focus'},
     {'dev': 'mth', 'name': 'mth (A1)'}, {'dev': 'mtt', 'name': 'mtt (A2)'}],
])

sample = ('Sample stage', [
    ['stx', 'sty', 'stz', 'sat'],
    ['sgx', 'sgy', {'dev': 'sth', 'name': 'sth (A3)'},
     {'dev': 'stt', 'name': 'stt (A4)'}],
])

analyzer = ('Analyzer', [
    [{'dev': 'ana', 'name': 'kf_soll'}, {'key': 'ana/focmode', 'name': 'Focus'},
     {'dev': 'ath', 'name': 'ath (A5)'}, {'dev': 'att', 'name': 'att (A6)'}],
])

collimation = ('Collimation and Lengths', [
    ['ca1', 'ca2', 'ca3', 'ca4'],
    [{'dev': 'lsm', 'name': 'Src->Mono'}, {'dev': 'lms', 'name': 'Mono->Samp'},
     {'dev': 'lsa', 'name': 'Samp->Ana'}, {'dev': 'lad', 'name': 'Samp->Det'}],
])

column1 = [filters, primary, sample, analyzer, collimation]

detector = ('Detector', [
    ['timer', 'mon1', 'mon2'],
    ['det1', 'det2'],
])

column2 = [detector]

devices = dict(
    Monitor = device('nicos.monitor.fl.Monitor',
                     title = 'PANDA status monitor',
                     loglevel = 'info',
                     server = 'pandasrv.panda.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     fontsize = 14,
                     valuefont = 'Luxi Mono',
                     layout = [[expcolumn], [column1, column2]],
                     notifiers = [],
                     warnings = [])
)
