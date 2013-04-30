#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Widgets for entering values of different NICOS parameter/value types.

The supported types are defined in `nicos.core.params`.
"""

from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QLineEdit, QDoubleValidator, QIntValidator, \
     QCheckBox, QWidget, QComboBox, QHBoxLayout, QLabel

from nicos.core import params


# XXX unit?

def create(parent, typ, curvalue, fmtstr=''):
    if isinstance(typ, params.oneof):
        return ComboWidget(parent, typ.vals, curvalue)
    elif isinstance(typ, params.oneofdict):
        return ComboWidget(parent, typ.vals.values(), curvalue)
    elif isinstance(typ, params.none_or):
        return CheckWidget(parent, typ.conv, curvalue)
    elif isinstance(typ, params.tupleof):
        return MultiWidget(parent, typ.types, curvalue)
    elif typ == params.limits:
        # XXX could use custom styling
        return MultiWidget(parent, (float, float), curvalue)
    elif isinstance(typ, params.floatrange):
        # XXX display from-to (at least in tooltip)
        return EditWidget(parent, float, curvalue, fmtstr or '%.4g',
                          minmax=(typ.fr, typ.to))
    elif isinstance(typ, params.intrange):
        # XXX display from-to (at least in tooltip)
        return EditWidget(parent, int, curvalue, fmtstr or '%.4g',
                          minmax=(typ.fr, typ.to))
    elif typ in (int, float, str):
        return EditWidget(parent, typ, curvalue, fmtstr or '%.4g')
    elif typ == bool:
        return ComboWidget(parent, [True, False], curvalue)
    elif typ == params.vec3:
        return MultiWidget(parent, (float, float, float), curvalue)
    elif typ in (params.tacodev, params.tangodev, params.mailaddress,
                 params.control_path_relative):
        # XXX validate via regexp
        return EditWidget(parent, str, curvalue)
    return MissingWidget(parent, curvalue)
    # XXX missing: listof, nonemptylistof, dictof, ANYTYPE (->expression)


class MultiWidget(QWidget):

    def __init__(self, parent, types, curvalue):
        QWidget.__init__(self, parent)
        layout = QHBoxLayout()
        self._widgets = []
        for (typ, val) in zip(types, curvalue):
            widget = create(self, typ, val)
            self._widgets.append(widget)
            layout.addWidget(widget)
        self.setLayout(layout)

    def getValue(self):
        return tuple(w.getValue() for w in self._widgets)

class ComboWidget(QComboBox):

    def __init__(self, parent, values, curvalue):
        QComboBox.__init__(self, parent)
        self._textvals = map(str, values)
        self._values = values
        self.addItems(self._textvals)
        if curvalue in values:
            self.setCurrentIndex(values.index(curvalue))

    def getValue(self):
        return self._values[self._textvals.index(str(self.currentText()))]

class EditWidget(QLineEdit):

    def __init__(self, parent, typ, curvalue, fmtstr='%.4g', minmax=None):
        QLineEdit.__init__(self, parent)
        self._typ = typ
        if typ is float:
            val = QDoubleValidator(self)
            if minmax:
                val.setRange(minmax[0], minmax[1])
            self.setValidator(val)
            self.setText(fmtstr % curvalue)
        elif typ is int:
            val = QIntValidator(self)
            if minmax:
                val.setRange(minmax[0], minmax[1])
            self.setValidator(val)
            self.setText(str(curvalue))
        else:
            self.setText(str(curvalue))

    def getValue(self):
        return self._typ(self.text())

    # def sizeHint(self):
    #     sh = QLineEdit.sizeHint(self)
    #     sh.setWidth(sh.width()/2)
    #     return sh

class CheckWidget(QWidget):

    def __init__(self, parent, inner, curvalue):
        QWidget.__init__(self, parent)
        layout = QHBoxLayout()
        self.checkbox = QCheckBox(self)
        if curvalue is not None:
            self.checkbox.setCheckState(Qt.Checked)
        if curvalue is None:
            curvalue = inner()  # generate a dummy value
        self.inner_widget = create(self, inner, curvalue)
        self.inner_widget.setEnabled(self.checkbox.isChecked())
        layout.addWidget(self.checkbox)
        layout.addWidget(self.inner_widget)
        self.connect(self.checkbox, SIGNAL('stateChanged(int)'),
                     self.on_checkbox_stateChanged)
        # XXX deactivate inner on uncheck
        self.setLayout(layout)

    def on_checkbox_stateChanged(self, state):
        self.inner_widget.setEnabled(state == Qt.Checked)

    def getValue(self):
        if self.checkbox.isChecked():
            return self.inner_widget.getValue()
        return None

class MissingWidget(QLabel):

    def __init__(self, parent, curvalue):
        QLabel.__init__(self, parent)
        self.setText('(editing impossible)')
        self._value = curvalue

    def getValue(self):
        return self._value
