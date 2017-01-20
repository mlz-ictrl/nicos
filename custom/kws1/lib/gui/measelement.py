#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Helpers for commandlets for KWS(-1)."""

import re

from PyQt4.QtGui import QComboBox, QCheckBox, QLineEdit, QWidget, QSpinBox, \
    QHBoxLayout
from PyQt4.QtCore import QObject, pyqtSignal, SIGNAL

from nicos.guisupport import typedvalue
from nicos.guisupport.utils import DoubleValidator


def num_sort(x):
    """A sort key function to sort by a numeric prefix, then lexically."""
    m = re.match(r'[\d.]+', x)
    return (float(m.group()), x) if m else (99.0, '')


class MeasElement(QObject):
    """Represents one setting for a measurement that can be manipulated."""

    LABEL = ''
    ORDER = 1

    changed = pyqtSignal(object)

    def __init__(self, eltype, client, value=None, extra=None):
        """Initialize widget contents, if necessary."""
        QObject.__init__(self)
        self.eltype = eltype
        self.value = value
        self.extra = extra
        self._widget = None
        self.clientUpdate(client)

    def getLabel(self):
        """Return label for the element."""
        if self.LABEL:
            return self.LABEL
        return self.eltype.capitalize()

    def clientUpdate(self, client):
        """Update internal info from daemon."""

    def createWidget(self, parent, client):
        """Create and return a Qt widget for editing this element."""

    def destroyWidget(self):
        """Destroy the currently created widget."""
        if self._widget:
            self._widget.deleteLater()
            self._widget = None

    def getValue(self):
        """Return currently selected value."""
        return self.value

    def getDispValue(self):
        """Return a form of the value to be displayed."""
        return str(self.getValue())

    def otherChanged(self, eltype, value):
        """Hook to be called when a sibling element changed."""


class ChoiceElement(MeasElement):
    """Base for elements that allow an arbitrary choice."""

    CACHE_KEY = ''
    VALUES = []

    def createWidget(self, parent, client):
        if self.CACHE_KEY:
            values = client.getDeviceParam(*self.CACHE_KEY.split('/'))
            values = sorted(values or [], key=num_sort)
        else:
            values = self.VALUES
        self._values = values
        self._widget = QComboBox(parent)
        self._widget.addItems(self._values)
        if self.value is not None and self.value in self._values:
            self._widget.setCurrentIndex(self._values.index(self.value))
        elif self.value is None and self._values:
            self.value = self._values[0]
        self._widget.currentIndexChanged.connect(self._updateValue)
        return self._widget

    def _updateValue(self, index):
        self.value = self._values[index]
        self.changed.emit(self.value)


class CheckElement(MeasElement):
    """Base for elements that allow yes/no choice."""

    def createWidget(self, parent, client):
        self._widget = QCheckBox(parent)
        if self.value is None:
            self.value = False
        self._widget.setChecked(self.value)
        self._widget.toggled.connect(self._updateValue)
        return self._widget

    def _updateValue(self, checked):
        self.value = checked
        self.changed.emit(self.value)

    def getDispValue(self):
        return 'yes' if self.value else 'no'


class FloatElement(MeasElement):
    """Base for elements that are floating point numbers."""

    def createWidget(self, parent, client):
        if self.value is None:
            self.value = 10.0
        self._widget = QLineEdit(parent)
        self._widget.setValidator(DoubleValidator(parent))
        self._widget.setText('%g' % self.value)
        self._widget.textChanged.connect(self._updateValue)
        return self._widget

    def _updateValue(self, text):
        self.value = float(text.replace(',', '.'))
        self.changed.emit(self.value)


class Detector(MeasElement):
    """Element for selecting detector distance, depending on selector."""

    CACHE_KEY = 'detector/presets'
    LABEL = 'Detector'

    _allvalues = None

    def clientUpdate(self, client):
        self._allvalues = client.getDeviceParam(*self.CACHE_KEY.split('/'))
        self._values = []

    def createWidget(self, parent, client):
        self.clientUpdate(client)
        self._widget = QComboBox(parent)
        self._updateWidget()
        self._widget.currentIndexChanged.connect(self._updateValue)
        return self._widget

    def _updateWidget(self):
        self._widget.clear()
        self._widget.addItems(self._values)
        if self.value in self._values:
            self._widget.setCurrentIndex(self._values.index(self.value))

    def otherChanged(self, eltype, value):
        if eltype == 'selector' and self._allvalues is not None:
            self._values = sorted(self._allvalues[value], key=num_sort)
            if self.value not in self._values:
                if self._values:
                    self.value = self._values[0]
                else:
                    self.value = None
            if self._widget is not None:
                self._updateWidget()

    def _updateValue(self, index):
        self.value = self._values[index]
        self.changed.emit(self.value)


class Chopper(MeasElement):
    """Element for selecting chopper TOF resolution."""

    CACHE_KEY = 'chopper/resolutions'
    LABEL = u'TOF dλ/λ'

    def createWidget(self, parent, client):
        resos = client.getDeviceParam(*self.CACHE_KEY.split('/'))
        self._values = ['off'] + ['%.1f%%' % v
                                  for v in (resos or [])] + ['manual']
        self._widget = QComboBox(parent)
        self._widget.addItems(self._values)
        if self.value is not None and self.value in self._values:
            self._widget.setCurrentIndex(self._values.index(self.value))
        elif self.value is None and self._values:
            self.value = self._values[0]
        self._widget.currentIndexChanged.connect(self._updateValue)
        return self._widget

    def _updateValue(self, index):
        self.value = self._values[index]
        self.changed.emit(self.value)


class Selector(ChoiceElement):
    CACHE_KEY = 'selector/mapping'
    LABEL = 'Selector'


class Polarizer(ChoiceElement):
    CACHE_KEY = 'polarizer/values'
    LABEL = 'Polarizer'


class Lenses(ChoiceElement):
    CACHE_KEY = 'lenses/values'
    LABEL = 'Lenses'


class Collimation(ChoiceElement):
    CACHE_KEY = 'collimation/mapping'
    LABEL = 'Collimation'


class MeasTime(MeasElement):
    """Element for selecting measurement time in different time units."""

    LABEL = 'Time'

    def createWidget(self, parent, client):
        if self.value is None:
            self.value = 30 * 60
        self._widget = QWidget(parent)
        layout = QHBoxLayout()
        self._widget.number = QSpinBox(self._widget)
        self._widget.number.setValue(30)
        self._widget.number.setMaximum(10000)
        self._widget.unit = QComboBox(self._widget)
        self._widget.unit.addItems(['sec', 'min', 'hr'])
        self._widget.unit.setCurrentIndex(1)
        layout.addWidget(self._widget.number)
        layout.addWidget(self._widget.unit)
        layout.setContentsMargins(0, 0, 0, 0)
        self._widget.setLayout(layout)
        self._widget.number.valueChanged.connect(self._updateValue)
        self._widget.unit.currentIndexChanged.connect(self._updateValue)
        self._widget.setMinimumWidth(120)
        if self.value is not None:
            if self.value % 3600 == 0:
                self._widget.number.setValue(self.value / 3600)
                self._widget.unit.setCurrentIndex(2)
            elif self.value % 60 == 0:
                self._widget.number.setValue(self.value / 60)
                self._widget.unit.setCurrentIndex(1)
            else:
                self._widget.number.setValue(self.value)
                self._widget.unit.setCurrentIndex(0)
        return self._widget

    def _updateValue(self, *args):
        unit = self._widget.unit.currentIndex()
        number = self._widget.number.value()
        if unit == 0:
            self.value = number
        elif unit == 1:
            self.value = number * 60
        else:
            self.value = number * 3600
        self.changed.emit(self.value)

    def getDispValue(self):
        # TODO: better display here
        if self.value % 3600 == 0:
            return '%d hr' % (self.value / 3600)
        elif self.value % 60 == 0:
            return '%d min' % (self.value / 60)
        else:
            return '%d sec' % self.value


class Sample(ChoiceElement):
    CACHE_KEY = 'exp/samples'
    LABEL = 'Sample'
    ORDER = 0


class Device(MeasElement):
    """Element to select the value for a device.

    eltype is set to the device name.
    """

    ORDER = 2

    def getLabel(self):
        return self.eltype

    def clientUpdate(self, client):
        self._valuetype = client.getDeviceValuetype(self.eltype)
        if self.value is None:
            self.value = self._valuetype()

    def createWidget(self, parent, client):
        self._widget = typedvalue.create(parent, self._valuetype, self.value,
                                         allow_enter=False)
        self.connect(self._widget, SIGNAL('dataChanged'), self._updateValue)
        return self._widget

    def _updateValue(self):
        self.value = self._widget.getValue()
        self.changed.emit(self.value)
