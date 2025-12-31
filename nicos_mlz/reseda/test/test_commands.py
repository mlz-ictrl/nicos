# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""RESEDA MIEZE calculation tests."""

from pathlib import Path

import pytest

from nicos_mlz.reseda.commands import img, miezetau, pol, tof
from nicos_mlz.reseda.tuning_commands import ExportTuning, ImportTuning

from test.utils import ErrorLogged

session_setup = 'reseda'


class TestCommands:

    def test_miezetau(self):

        for f, r in [(1, 1e-6), (10, 1e-5), (100, 1e-4), (1000, 1e-3)]:
            assert pytest.approx(miezetau(4.5, f, 3)) == 3.4935644 * r
            assert pytest.approx(miezetau(6.0, f, 3)) == 8.2810416 * r

    def test_tof(self, session):
        tof()
        assert session.getDevice('psd_channel').mode == 'tof'

    def test_img(self, session):
        img()
        assert session.getDevice('psd_channel').mode == 'image'

    def test_pol(self, session):
        assert pol(1, 2) == pytest.approx(-0.3333, abs=0.0001)
        assert pol(2, 1) == pytest.approx(0.3333, abs=0.0001)

        pytest.raises(ZeroDivisionError, pol, 0, 0)

    def test_tuning(self, session):
        pytest.raises(ErrorLogged, ImportTuning, 'mieze', 6,
                      '1020_02_07_mcstas')
        pytest.raises(ErrorLogged, ImportTuning, 'mieze',
                      6, '2019_02_07_fail')
        ImportTuning('mieze', 6, filename='2019_02_07_mcstas')
        table = session.getDevice('echotime').getTable('mieze', 6)
        assert list(table.keys()) == [
            6.85e-06, 3.42e-05, 6.85e-05, 0.000205, 0.000685, 0.00123, 0.00219,
            0.00301, 0.00411, 0.00473, 0.00534, 0.00685, 0.0076, 0.00836,
            0.00932, 0.0103, 0.0112, 0.012, 0.0137, 0.0155, 0.0173, 0.0195,
            0.0216, 0.0235, 0.0253, 0.0296, 0.0329, 0.0371, 0.0501, 0.0707,
            0.0891, 0.109, 0.148, 0.182, 0.215, 0.249, 0.283, 0.327, 0.372,
            0.417, 0.462, 0.531, 0.582, 0.634, 0.685, 0.728, 0.771, 0.805,
            0.908, 0.939, 1.06, 1.17, 1.28, 1.37, 1.49, 1.6, 1.67, 2.71, 3.95,
            5.95, 11.7, 13.4, 2.48]
        ExportTuning('mieze', 6, filename='2019_02_07_2_mcstas')
        pytest.raises(ErrorLogged, ExportTuning, 'miez', 6,
                      '2019_02_07_2_mcstas')
        pytest.raises(ErrorLogged, ExportTuning, 'mieze', 16,
                      '2019_02_07_2_mcstas')
        pytest.raises(ErrorLogged, ExportTuning, 'mieze', 6,
                      '2019_02_07_2_mcstas')
        Path(session.experiment.dataroot,
             '2019_02_07_2_mcstas_mieze_6A.csv').unlink()
