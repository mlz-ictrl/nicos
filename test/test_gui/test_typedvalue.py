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

"""NICOS test lib: Test typed value widgets """


import pytest

from nicos.guisupport.typedvalue import ButtonWidget, ComboWidget, \
    EditWidget, ExprWidget, MissingWidget, Qt, SpinBoxWidget

pytest.importorskip('pytestqt')


class TestTypedvalue:

    @pytest.mark.parametrize('typ,initvalue,inputs,result', [
        (str, 'value', ['text'], 'text'),
        (int, 0, [42, 'text'], 42),
        (float, 0, [4.2, 'txt'], 4.2),
    ])
    def test_EditWidget(self, qtbot, typ, initvalue, inputs, result):
        widget = EditWidget(None, typ, initvalue, allow_enter=True)
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        widget.clear()
        for text in inputs:
            qtbot.keyClicks(widget, str(text))
        assert widget.getValue() == result

    @pytest.mark.parametrize('add_other', [True, False])
    def test_ComboWidget(self, qtbot, add_other):
        widget = ComboWidget(None, [1, 2, 4], 2, add_other=True)
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        assert widget.getValue() == 2
        widget.setCurrentIndex(0)
        assert widget.getValue() == 1

    def test_ButtonWidget(self, qtbot):
        widget = ButtonWidget(None, ['in', 'out'])
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        for i in range(widget.layout().count()):
            w = widget.layout().itemAt(i).widget()
            qtbot.mouseClick(w, Qt.LeftButton)

        assert widget.getValue() == Ellipsis

    def test_SpinboxWidget(self, qtbot):
        widget = SpinBoxWidget(None, 1, [0, 10], allow_enter=True)
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        assert widget.getValue() == 1

    def test_MissingWidget(self, qtbot):
        widget = MissingWidget(None, 2)
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        assert widget.getValue() == 2

    def test_ExprWidget(self, qtbot):
        widget = ExprWidget(None, 1, allow_enter=True)
        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        assert widget.getValue() == 1

        widget.clear()
        qtbot.keyClicks(widget, str(2))
        assert widget.getValue() == 2
