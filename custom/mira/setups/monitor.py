#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS monitor setup file with a few devices
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

name = 'setup for the status monitor'
group = 'special'

_reactor = [
]

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
    ('Slits', [[{'dev': 's3', 'name': 'Slit 3', 'width': 24, 'istext': True}],
               [{'dev': 's4', 'name': 'Slit 4', 'width': 24, 'istext': True}]],
     'slits'),
    ('X-Z table axes', [[{'dev': 'mx'}, {'dev': 'my'}]], 'gauss'),
]

_column2 = [
    ('Detector', [
        ['timer', 'ctr1', 'mon1'],
        '---',
        [{'dev': 'MonHV', 'name': 'Mon HV', 'min': 490, 'width': 5},
         {'dev': 'DetHV', 'name': 'Det HV', 'min': 840, 'width': 5},
         {'dev': 'PSDHV', 'name': 'PSD HV', 'min': 2800, 'width': 5}],
        ],
     'detector'),
    ('Cascade', [
        [{'dev': 'psd', 'name': 'ROI', 'item': 0, 'width': 9},
         {'dev': 'psd', 'name': 'Total', 'item': 1, 'width': 9},
         {'key': 'psd/lastfilenumber', 'name': 'Last file'}],
        ],
     'cascade'),
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
     'detector'),
    ('Reactor', [
        [{'dev': 'Power', 'name': 'Power', 'min': 19, 'format': '%d', 'width': 7},
         {'dev': 'Sixfold', 'name': '6-fold', 'min': 'open', 'width': 7},
         {'dev': 'NL6', 'name': 'NL6', 'min': 'open', 'width': 7}],
    ], 'reactor'),
]

_warnings = [
#    ('psdhv/value', '== 0', 'PSD HV switched off'),
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
