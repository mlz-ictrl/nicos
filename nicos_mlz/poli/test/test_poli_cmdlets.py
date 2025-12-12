# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

"""Poli tests: Test cmdlets."""

from nicos.guisupport.qt import Qt

from nicos_mlz.poli.gui.cmdlets import CenterPeak, Lubrication

# , RefineMatrix

from test.test_gui.test_cmdlets import CmdletTester

session_setup = ''


class TestCenterPeak(CmdletTester):

    cls = CenterPeak

    def test_inited(self, widget):
        assert widget.isValid()
        assert widget.getValues() == {
            'dev': 'gax',
            'counttime': 1.0,
        }
        assert widget.generate() == \
            'centerpeak(gax, steps=15, step=0.1, rounds=5, t=1.0)'

    def test_set_values(self, widget):
        widget.setValues({'dev': 'gax'})
        widget.isValid()

        widget.func.setCurrentText('gauss')
        assert widget.isValid()
        assert widget.generate() == \
            "centerpeak(gax, steps=15, step=0.1, rounds=5, fit='gauss', t=1.0)"

        widget.contBox.setChecked(Qt.Checked)
        assert widget.isValid()
        assert widget.generate() == \
            "centerpeak(gax, steps=15, step=0.1, rounds=5, fit='gauss', t=1.0, cont=True)"


class TestLubrication(CmdletTester):

    cls = Lubrication

    def test_inited(self, widget):
        assert not widget.isValid()
        assert widget.getValues() == {
        }
        assert widget.generate() == 'lubricate_liftingctr(, )'

    def test_set_values(self, widget):
        widget.start.setText('10')
        widget.end.setText('20')
        assert widget.isValid()
        assert widget.generate() == 'lubricate_liftingctr(10, 20)'


# class TestRefineMatrix(CmdletTester):
#
#     cls = RefineMatrix
#
#     def test_inited(self, widget):
#         assert widget.isValid()
#         assert widget.getValues() == {
#         }
#         assert widget.generate() == \
#             ""
