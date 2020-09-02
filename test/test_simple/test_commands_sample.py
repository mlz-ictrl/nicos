#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
from io import StringIO

import mock

from nicos.commands.sample import activation, powderfit
from nicos.commands.scan import cscan
from nicos.core import UsageError

from test.utils import approx, raises

session_setup = 'tas'


# pylint: disable=line-too-long

H2_RESPONSE = {'pdfurl': 'https://webapps.frm2.tum.de/intranet/activation/activation.pdf/', 'curr': 'Manual', 'shield': '1', 'url': 'https://www.frm2.tum.de/intranet/activation//', 'instruments': ['BIODIFF', 'HEIDI', 'MIRA', 'MIRA2', 'POLI', 'RESI', 'SPODI', 'STRESSPEC', 'KWS1', 'KWS2', 'KWS3', 'MARIA', 'NREX', 'REFSANS', 'SANS1', 'DNS', 'JNSE', 'PANDA', 'PUMA', 'RESEDA', 'SPHERES', 'TOFTOF', 'TRISP', 'ANTARES@L/D=800', 'NECTAR', 'PGAA', 'MEPHISTO'], 'showinput': True, 'sampleid': '', 'ecode': 'unknown instrument', 'formula': 'H2', 'flux': {'fast_ratio': 0.0, 'Cd_ratio': 0.0, 'fluence': 20.0}, 'proposalid': '', 'tunit': 'h', 'result': {'comp': [['H', 2]], 'activation': None, 'mass': 2.01588, 'weightperc': [['H', 1.0]], 'decay': None}, 'error': None, 'mass': '1', 'pversion': '2.19', 'exposure': '24'}

AU_RESPONSE = {'pdfurl': 'https://webapps.frm2.tum.de/intranet/activation/activation.pdf/', 'curr': 'Manual', 'shield': '1', 'url': 'https://www.frm2.tum.de/intranet/activation//', 'instruments': ['BIODIFF', 'HEIDI', 'MIRA', 'MIRA2', 'POLI', 'RESI', 'SPODI', 'STRESSPEC', 'KWS1', 'KWS2', 'KWS3', 'MARIA', 'NREX', 'REFSANS', 'SANS1', 'DNS', 'JNSE', 'PANDA', 'PUMA', 'RESEDA', 'SPHERES', 'TOFTOF', 'TRISP', 'ANTARES@L/D=800', 'NECTAR', 'PGAA', 'MEPHISTO'], 'showinput': True, 'sampleid': '', 'ecode': 'unknown instrument', 'formula': 'Au', 'flux': {'fast_ratio': 0.0, 'Cd_ratio': 0.0, 'fluence': 10000000.0}, 'proposalid': '', 'tunit': 'h', 'result': {'decaytime3': 825.5259528186107, 'decay': {'rows': [{'gw': 100.0, 'activities': [683913.4455697088, 683913.4455697088, 100.00000000064743, 100.00000000064743], 'rest_times': [0, 0, 825.5259528186107, 825.5259528186107], 'daughter': 'Au-198', 'reaction': 'act', 'gwl': 100.0, 'isotope': 'Au-197', 'fg2l': 100.0, 'Thalf_str': '2.7 d', 'fg2': 100.0, 'fg': 1000000.0, 'Thalf_hrs': 64.8, 'relevant_activity': None, 'gwmax': 1000000.0, 'mode': 'B-, G'}], 'shield': 1.0, 'decaytime3': 825.5259528186107, 'decaytime2': 0, 'sdoses': [0.014770729782154466, 0.014770729782154466, 2.159736714920977e-06, 2.159736714920977e-06], 'resttimes': [0, 0, 825.5259528186107, 825.5259528186107], 'totals': [683913.4455697088, 683913.4455697088, 100.00000000064743, 100.00000000064743], 'headers': {'gw': 'limit (Bq/g)', 'activities': ['A@0.0 h', 'A@0.0 h', 'A@1.1 M', 'A@1.1 M'], 'daughter': 'Daughter', 'reaction': 'reaction', 'sdoses': 'Dose (1.0 cm Pb)', 'fg': 'limit2 (Bq)', 'isotope': 'Isotope', 'Thalf_str': 'T1/2', 'gwl': 'limit@mass', 'fg2': 'limit3 (Bq/g)', 'doses': 'Dose (\xb5Sv/h)', 'total': 'total', 'mode': 'mode'}, 'rtl': 4, 'doses': [0.3524322326724863, 0.3524322326724863, 5.153170111770319e-05, 5.153170111770319e-05], 'decaytime': 825.5259528186107}, 'comp': [['Au', 1]], 'activation': {'rows': [{'gw': 100.0, 'activities': [683913.4455697088, 676636.8053040033, 529064.4140130356, 18797.70666063267], 'rest_times': [0, 1, 24, 336], 'daughter': 'Au-198', 'reaction': 'act', 'gwl': 100.0, 'isotope': 'Au-197', 'fg2l': 100.0, 'Thalf_str': '2.7 d', 'fg2': 100.0, 'fg': 1000000.0, 'Thalf_hrs': 64.8, 'relevant_activity': 529064.4140130356, 'gwmax': 1000000.0, 'mode': 'B-, G'}], 'shield': 1.0, 'decaytime3': 825.5259528186107, 'decaytime2': 0, 'sdoses': [0.014770729782154466, 0.014613573510724313, 0.011426398394947072, 0.00040598097231020133], 'resttimes': [0, 1, 24, 336], 'totals': [683913.4455697088, 676636.8053040033, 529064.4140130356, 18797.70666063267], 'headers': {'gw': 'limit (Bq/g)', 'activities': ['A@0.0 h', 'A@1.0 h', 'A@24.0 h', 'A@14.0 d'], 'daughter': 'Daughter', 'reaction': 'reaction', 'sdoses': 'Dose (1.0 cm Pb)', 'fg': 'limit2 (Bq)', 'isotope': 'Isotope', 'Thalf_str': 'T1/2', 'gwl': 'limit@mass', 'fg2': 'limit3 (Bq/g)', 'doses': 'Dose (\xb5Sv/h)', 'total': 'total', 'mode': 'mode'}, 'rtl': 4, 'doses': [0.3524322326724863, 0.3486824561593767, 0.27263589254756015, 0.009686778013277096], 'decaytime': 825.5259528186107}, 'decaytime2': 0, 'weightperc': [['Au', 1.0]], 'mass': 196.96655, 'decaytime': 825.5259528186107, 'tpcl': 0}, 'error': None, 'mass': '1', 'pversion': '2.19', 'exposure': '24'}


def mock_open_H2(url):
    return StringIO(json.dumps(H2_RESPONSE))


def mock_open_Au(url):
    return StringIO(json.dumps(AU_RESPONSE))


def test_activation_wronginput(log):
    with mock.patch('urllib.request.urlopen', new=mock_open_H2):
        assert raises(UsageError, activation)  # session has no formula up to now
        assert raises(UsageError, activation, formula='H2O')
        assert raises(UsageError, activation, formula='H2O', flux=1e7)
        with log.assert_warns():
            activation(formula='H2', instrument='IN', mass=1)


def test_activation_function():
    with mock.patch('urllib.request.urlopen', new=mock_open_H2):
        data = activation(formula='H2', flux=20, mass=1, getdata=True)
        assert data['curr'] == 'Manual'
        assert data['flux']['fluence'] == 20
        assert data['result']['activation'] is None
    with mock.patch('urllib.request.urlopen', new=mock_open_Au):
        data = activation(formula='Au', flux=1e7, mass=1, getdata=True)
        assert data['result']['activation'] is not None


def test_powderfit_from_peaks():
    res = powderfit('YIG', ki=1.32, peaks=[55.22, 64.91, 91.04, 99.58])
    assert res[0] == approx(0.02, abs=1e-2)
    assert res[1] == approx(-1, abs=1e-2)


def test_powderfit_from_data(session):
    tasdev = session.getDevice('Tas')
    tasdev.scanconstant = 2.0
    sample = session.getDevice('Sample')
    phidev = session.getDevice('t_phi')
    tasdet = session.getDevice('vtasdet')
    sample.lattice = [12.38, 12.38, 12.38]
    sample.orient1 = [1, 0, 0]
    sample.orient2 = [0, 1, 1]
    peaks = [(4, 0, 0, 0), (2, 1, 1, 0), (0, 2, 2, 0)]
    for peak in peaks:
        tasdev.maw(peak)
        cscan(phidev, phidev(), 0.2, 10, 1, tasdet)
    # since datasets are not numbered (no sink), number 0 will catch all
    res = powderfit('YIG', scans=[0])
    assert -0.105 <= res[0] <= 0.105
    assert -0.105 <= res[1] <= 0.105
