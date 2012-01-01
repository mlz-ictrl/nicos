#  -*- coding: utf-8 -*-

name = 'setup for the status monitor'
group = 'special'

_exp = [('Experiment', [[{'key': 'exp/proposal', 'name': 'Proposal'},
                          {'key': 'exp/title', 'name': 'Title', 'istext': True, 'width': 40},
                          {'key': 'filesink/lastfilenumber', 'name': 'Last file number'}]])]

_row1 = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']

_row2 = ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8']

_row3 = ['p1',  'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8']


_block1 = ('Motorrahmen Test', [_row1, _row2, _row3], 'testaxes')

_column1 = [
    _block1,
    _block1,
    #_block2,
    #_block3,
]

devices = dict(
    Monitor = device('nicos.monitor.fl.Monitor',
                     title = 'PANDA status monitor',
                     loglevel = 'info',
                     server = 'pandasrv',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     fontsize = 10,
                     valuefont = 'Luxi Mono',
                     layout = [[_column1, _column1]])
)
