# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

"""NICOS test lib: Test PGAA widgets """

import pytest

pytest.importorskip('pytestqt')
pytest.importorskip('OpenGL')

from nicos_mlz.pgaa.gui.panels.widgets import AttCell, BeamCell, CondCell, \
    DetectorCell, ElColCell, NameCommentCell, PosCell, StartCell, StatusCell, \
    TimeEditWidget, ValueCell


class TestWidgets:

    def test_attcell(self, qtbot):
        widget = AttCell(None)
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        assert widget.value() == 100.
        widget.setValue(16)
        assert widget.value() == 16.

    def test_beamcell(self, qtbot):
        widget = BeamCell(None)
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        assert widget.value() == 'open'
        widget.setValue('closed')
        assert widget.value() == 'closed'

    def test_condcell(self, qtbot):
        widget = CondCell(None, state='TrueTime')
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        assert widget.value() == 'TrueTime'
        widget.setValue('LiveTime')
        assert widget.value() == 'LiveTime'

    def test_detectorcell(self, qtbot):
        widget = DetectorCell(None, state=[])
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        assert widget.value() == []  # pylint: disable=use-implicit-booleaness-not-comparison
        for v in ['_60p', 'LEGe']:
            widget.setValue(v)
            assert widget.value() == [v]

    def test_elcolcell(self, qtbot):
        widget = ElColCell(None)
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        assert widget.value() == 'Col'
        widget.setValue('Ell')
        assert widget.value() == 'Ell'

    def test_namecommentcell(self, qtbot):
        widget = NameCommentCell(None)
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        assert widget.value() == ''
        widget.setValue('test')
        assert widget.value() == 'test'

    def test_poscell(self, qtbot):
        widget = PosCell(None, state=1)
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        assert widget.value() == 1
        widget.setValue(16)
        assert widget.value() == 16

    def test_startcell(self, qtbot):
        widget = StartCell(None)
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        assert widget.value()[-3:] == ',0]'

    def test_statuscell(self, qtbot):
        widget = StatusCell(None)
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

    def test_timeeditwidget(self, qtbot):
        widget = TimeEditWidget(None)
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

    def test_valuecell(self, qtbot):
        widget = ValueCell(None)
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        assert widget.value() == 1.
        widget.setValue(2)
        assert widget.value() == 2.
