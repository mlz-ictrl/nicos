#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#
#   Ebad Kamil <Ebad.Kamil@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
"""Useful delegates for tables."""
from nicos.guisupport.qt import QAbstractSpinBox, QComboBox, QDoubleSpinBox, \
    QItemDelegate


class LimitsDelegate(QItemDelegate):

    def __init__(self, limits=(0, 0), precision=3):
        QItemDelegate.__init__(self)
        self.limits = limits
        self.precision = precision

    def createEditor(self, parent, option, index):
        return self._create_widget(parent)

    def _create_widget(self, parent):
        spinbox = QDoubleSpinBox(parent)
        spinbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        spinbox.setMinimum(self.limits[0])
        spinbox.setMaximum(self.limits[1])
        spinbox.setDecimals(self.precision)
        return spinbox


class ReadOnlyDelegate(QItemDelegate):

    def createEditor(self, parent, option, index):
        return None


class ComboBoxDelegate(QItemDelegate):

    def __init__(self):
        QItemDelegate.__init__(self)
        self.items = []

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.items)
        return editor
