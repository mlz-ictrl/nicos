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

from nicos.core.params import dictof, dictwith, limits, listof, none_or, \
    setof, tupleof
from nicos.guisupport.typedvalue import ButtonWidget, CheckWidget, \
    ComboWidget, DeviceComboWidget, DictOfWidget, DictWithWidget, EditWidget, \
    ExprWidget, LimitsWidget, ListOfWidget, MissingWidget, MultiWidget, Qt, \
    SetOfWidget, SpinBoxWidget

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

    @pytest.mark.parametrize('curvalue', [True, False])
    def test_DictWithWidget(self, qtbot, curvalue):
        typ = dictwith(key=bool)

        widget = DictWithWidget(None, typ.convs.keys(), typ.convs.values(),
                                {'key': curvalue}, None, allow_enter=True)
        qtbot.addWidget(widget)
        widget.show()
        with qtbot.waitExposed(widget):
            pass

        assert widget.getValue() == {'key': curvalue}

    def test_DictOfWidget(self, qtbot):
        typ = dictof(str, float)

        res = {'blah': 0.1}
        widget = DictOfWidget(None, typ.keyconv, typ.valconv, res,
                              None, allow_enter=True)
        qtbot.addWidget(widget)
        widget.show()
        with qtbot.waitExposed(widget):
            pass

        assert widget.getValue() == res

        for i, (k, v) in enumerate((('point', 1), ('slit', 2), ('gisans', 3))):
            qtbot.mouseClick(widget.addBtn, Qt.LeftButton)
            assert widget.getValue() == {**res, **{'': 0.0}}

            widget.items[i + 1]._widgets[0].setText(k)
            assert widget.getValue() == {**res, **{k: 0.0}}

            widget.items[i + 1]._widgets[2].setText(f'{v}')
            assert widget.getValue() == {**res, **{k: v}}

            res.update({k: v})

    def test_ListOfWidget(self, qtbot):
        typ = listof(str)

        widget = ListOfWidget(None, typ.conv, ('one', 'two', 'three', ), None,
                              allow_enter=True)
        qtbot.addWidget(widget)
        widget.show()
        with qtbot.waitExposed(widget):
            pass

        assert widget.getValue() == ['one', 'two', 'three']

        arrow_up = 1
        arrow_down = 2
        delete = 3

        # Last entry move up
        qtbot.mouseClick(
            widget.items[2].layout().itemAt(arrow_up).widget(), Qt.LeftButton)
        assert widget.getValue() == ['one', 'three', 'two']

        # Second entry move down
        qtbot.mouseClick(
            widget.items[1].layout().itemAt(arrow_down).widget(), Qt.LeftButton)
        assert widget.getValue() == ['one', 'two', 'three']

        # Remove last entry
        qtbot.mouseClick(
            widget.items[2].layout().itemAt(delete).widget(), Qt.LeftButton)
        assert widget.getValue() == ['one', 'two']

        # Move last entry down
        qtbot.mouseClick(
            widget.items[1].layout().itemAt(arrow_down).widget(), Qt.LeftButton)
        assert widget.getValue() == ['one', 'two']

        # Move first entry up
        qtbot.mouseClick(
            widget.items[0].layout().itemAt(arrow_up).widget(), Qt.LeftButton)
        assert widget.getValue() == ['one', 'two']

    def test_MultiWidget(self, qtbot):
        typ = tupleof(int, int, int, int, int, int)

        widget = MultiWidget(None, typ.types, (0, 1, 2, 4, 8, 16), None,
                             allow_enter=True, valinfo=None)
        qtbot.addWidget(widget)
        widget.show()
        with qtbot.waitExposed(widget):
            pass

        assert widget.getValue() == (0, 1, 2, 4, 8, 16)

    def test_LimitsWidget(self, qtbot):
        widget = LimitsWidget(None, limits((0, 1)), None, allow_enter=True)
        qtbot.addWidget(widget)
        widget.show()
        with qtbot.waitExposed(widget):
            pass

        assert widget.getValue() == (0, 1)

    def test_SetOfWidget(self, qtbot):
        typ = setof('metadata', 'namespace', 'devlist')

        widget = SetOfWidget(None, typ.vals, {'metadata', 'namespace'}, None)
        qtbot.addWidget(widget)
        widget.show()
        with qtbot.waitExposed(widget):
            pass

        assert widget.getValue() == {'metadata', 'namespace'}

        for w in widget.checkboxes:
            w.setCheckState(Qt.CheckState.Checked)
        assert widget.getValue() == {'metadata', 'namespace', 'devlist'}

    @pytest.mark.parametrize('curvalue', [1, None])
    def test_CheckWidget(self, qtbot, curvalue):
        typ = none_or(int)

        widget = CheckWidget(None, typ.conv, curvalue, None)
        qtbot.addWidget(widget)
        widget.show()
        with qtbot.waitExposed(widget):
            pass

        assert widget.getValue() == curvalue

        if curvalue is not None:
            widget.checkbox.setCheckState(Qt.CheckState.Unchecked)
            assert widget.getValue() is None

    def test_DeviceComboWidget(self, qtbot):
        widget = DeviceComboWidget(None, 'device', None, allow_enter=True)
        qtbot.addWidget(widget)
        widget.show()
        with qtbot.waitExposed(widget):
            pass

        assert widget.getValue() == 'device'
