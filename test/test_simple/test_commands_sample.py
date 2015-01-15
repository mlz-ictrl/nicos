#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""NICOS commands tests."""

import json

import mock

from nicos import session
from nicos.core import UsageError
from nicos.commands.sample import activation
from nicos.pycompat import BytesIO

from test.utils import raises


# pylint: disable=C0301

H2_RESPONSE = {u'pdfurl': u'https://www.frm2.tum.de/intranet/activation/activation.pdf/', u'curr': u'Manual', u'shield': u'1', u'url': u'https://www.frm2.tum.de/intranet/activation//', u'instruments': [u'BIODIFF', u'HEIDI', u'MIRA', u'MIRA2', u'POLI', u'RESI', u'SPODI', u'STRESSPEC', u'KWS1', u'KWS2', u'KWS3', u'MARIA', u'NREX', u'REFSANS', u'SANS1', u'DNS', u'JNSE', u'PANDA', u'PUMA', u'RESEDA', u'SPHERES', u'TOFTOF', u'TRISP', u'ANTARES@L/D=800', u'NECTAR', u'PGAA', u'MEPHISTO'], u'showinput': True, u'sampleid': u'', u'ecode': u'unknown instrument', u'formula': u'H2', u'flux': {u'fast_ratio': 0.0, u'Cd_ratio': 0.0, u'fluence': 20.0}, u'proposalid': u'', u'tunit': u'h', u'result': {u'comp': [[u'H', 2]], u'activation': None, u'mass': 2.01588, u'weightperc': [[u'H', 1.0]], u'decay': None}, u'error': None, u'mass': u'1', u'pversion': u'2.19', u'exposure': u'24'}

AU_RESPONSE = {u'pdfurl': u'https://www.frm2.tum.de/intranet/activation/activation.pdf/', u'curr': u'Manual', u'shield': u'1', u'url': u'https://www.frm2.tum.de/intranet/activation//', u'instruments': [u'BIODIFF', u'HEIDI', u'MIRA', u'MIRA2', u'POLI', u'RESI', u'SPODI', u'STRESSPEC', u'KWS1', u'KWS2', u'KWS3', u'MARIA', u'NREX', u'REFSANS', u'SANS1', u'DNS', u'JNSE', u'PANDA', u'PUMA', u'RESEDA', u'SPHERES', u'TOFTOF', u'TRISP', u'ANTARES@L/D=800', u'NECTAR', u'PGAA', u'MEPHISTO'], u'showinput': True, u'sampleid': u'', u'ecode': u'unknown instrument', u'formula': u'Au', u'flux': {u'fast_ratio': 0.0, u'Cd_ratio': 0.0, u'fluence': 10000000.0}, u'proposalid': u'', u'tunit': u'h', u'result': {u'decaytime3': 825.5259528186107, u'decay': {u'rows': [{u'gw': 100.0, u'activities': [683913.4455697088, 683913.4455697088, 100.00000000064743, 100.00000000064743], u'rest_times': [0, 0, 825.5259528186107, 825.5259528186107], u'daughter': u'Au-198', u'reaction': u'act', u'gwl': 100.0, u'isotope': u'Au-197', u'fg2l': 100.0, u'Thalf_str': u'2.7 d', u'fg2': 100.0, u'fg': 1000000.0, u'Thalf_hrs': 64.8, u'relevant_activity': None, u'gwmax': 1000000.0, u'mode': u'B-, G'}], u'shield': 1.0, u'decaytime3': 825.5259528186107, u'decaytime2': 0, u'sdoses': [0.014770729782154466, 0.014770729782154466, 2.159736714920977e-06, 2.159736714920977e-06], u'resttimes': [0, 0, 825.5259528186107, 825.5259528186107], u'totals': [683913.4455697088, 683913.4455697088, 100.00000000064743, 100.00000000064743], u'headers': {u'gw': u'limit (Bq/g)', u'activities': [u'A@0.0 h', u'A@0.0 h', u'A@1.1 M', u'A@1.1 M'], u'daughter': u'Daughter', u'reaction': u'reaction', u'sdoses': u'Dose (1.0 cm Pb)', u'fg': u'limit2 (Bq)', u'isotope': u'Isotope', u'Thalf_str': u'T1/2', u'gwl': u'limit@mass', u'fg2': u'limit3 (Bq/g)', u'doses': u'Dose (\xb5Sv/h)', u'total': u'total', u'mode': u'mode'}, u'rtl': 4, u'doses': [0.3524322326724863, 0.3524322326724863, 5.153170111770319e-05, 5.153170111770319e-05], u'decaytime': 825.5259528186107}, u'comp': [[u'Au', 1]], u'activation': {u'rows': [{u'gw': 100.0, u'activities': [683913.4455697088, 676636.8053040033, 529064.4140130356, 18797.70666063267], u'rest_times': [0, 1, 24, 336], u'daughter': u'Au-198', u'reaction': u'act', u'gwl': 100.0, u'isotope': u'Au-197', u'fg2l': 100.0, u'Thalf_str': u'2.7 d', u'fg2': 100.0, u'fg': 1000000.0, u'Thalf_hrs': 64.8, u'relevant_activity': 529064.4140130356, u'gwmax': 1000000.0, u'mode': u'B-, G'}], u'shield': 1.0, u'decaytime3': 825.5259528186107, u'decaytime2': 0, u'sdoses': [0.014770729782154466, 0.014613573510724313, 0.011426398394947072, 0.00040598097231020133], u'resttimes': [0, 1, 24, 336], u'totals': [683913.4455697088, 676636.8053040033, 529064.4140130356, 18797.70666063267], u'headers': {u'gw': u'limit (Bq/g)', u'activities': [u'A@0.0 h', u'A@1.0 h', u'A@24.0 h', u'A@14.0 d'], u'daughter': u'Daughter', u'reaction': u'reaction', u'sdoses': u'Dose (1.0 cm Pb)', u'fg': u'limit2 (Bq)', u'isotope': u'Isotope', u'Thalf_str': u'T1/2', u'gwl': u'limit@mass', u'fg2': u'limit3 (Bq/g)', u'doses': u'Dose (\xb5Sv/h)', u'total': u'total', u'mode': u'mode'}, u'rtl': 4, u'doses': [0.3524322326724863, 0.3486824561593767, 0.27263589254756015, 0.009686778013277096], u'decaytime': 825.5259528186107}, u'decaytime2': 0, u'weightperc': [[u'Au', 1.0]], u'mass': 196.96655, u'decaytime': 825.5259528186107, u'tpcl': 0}, u'error': None, u'mass': u'1', u'pversion': u'2.19', u'exposure': u'24'}


def mock_open_H2(url):
    return BytesIO(json.dumps(H2_RESPONSE))

def mock_open_Au(url):
    return BytesIO(json.dumps(AU_RESPONSE))


def test_01wronginput():
    with mock.patch('nicos.pycompat.urllib.request.urlopen', new=mock_open_H2):
        assert raises(UsageError, activation)  # session has no formula up to now
        assert raises(UsageError, activation, formula='H2O')
        assert raises(UsageError, activation, formula='H2O', flux=1e7)
        assert session.testhandler.warns(activation, warns_clear=True,
                                         formula='H2', instrument='XXX', mass=1)


def test_02function():
    with mock.patch('nicos.pycompat.urllib.request.urlopen', new=mock_open_H2):
        data = activation(formula='H2', flux=20, mass=1, getdata=True)
        assert data['curr'] == 'Manual'
        assert data['flux']['fluence'] == 20
        assert data['result']['activation'] is None
    with mock.patch('nicos.pycompat.urllib.request.urlopen', new=mock_open_Au):
        data = activation(formula='Au', flux=1e7, mass=1, getdata=True)
        assert data['result']['activation'] is not None
