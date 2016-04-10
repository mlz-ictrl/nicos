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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Helpers for commandlets for KWS(-1)."""

from PyQt4.QtGui import QComboBox, QCheckBox, QLineEdit
from PyQt4.QtCore import pyqtSignal

from nicos.guisupport.utils import DoubleValidator


class MeasElement(object):
    """Represents one setting for a measurement that can be manipulated."""

    LABEL = ''

    def init(self, ename, client, value=None):
        """Initialize widget contents, if necessary."""
        self.ename = ename

    def getValue(self):
        """Return currently selected/entered value."""

    def _changed(self, *args):
        self.changed.emit(self.getValue())

    def othersChanged(self, ename, value):
        """Called when a sister element changed."""


class ChoiceElement(MeasElement, QComboBox):
    """Base for elements that allow an arbitrary choice."""

    CACHE_KEY = ''
    VALUES = []

    changed = pyqtSignal(object)

    def init(self, ename, client, value=None):
        MeasElement.init(self, ename, client, value)
        if self.CACHE_KEY:
            values = client.getDeviceParam(*self.CACHE_KEY.split('/'))
            values = list(values or [])
        else:
            values = self.VALUES
        self.addItems(values)
        if value is not None and value in values:
            self.setCurrentIndex(values.index(value))
        self.currentIndexChanged.connect(self._changed)

    def getValue(self):
        return self.currentText()


class CheckElement(MeasElement, QCheckBox):
    """Base for elements that allow yes/no choice."""

    changed = pyqtSignal(object)

    def init(self, ename, client, value=None):
        MeasElement.init(self, ename, client, value)
        if value is not None:
            if value == 'yes':
                value = True
            if value == 'no':
                value = False
            self.setChecked(value)
        self.toggled.connect(self._changed)

    def getValue(self):
        return self.isChecked() and 'yes' or 'no'


class FloatElement(MeasElement, QLineEdit):
    """Base for elements that are floating point numbers."""

    changed = pyqtSignal(object)

    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        self.setValidator(DoubleValidator(self))
        self.setText('10')  # XXX
        self.textChanged.connect(self._changed)

    def init(self, ename, client, value=None):
        MeasElement.init(self, ename, client, value)
        if value is not None:
            self.setText('%g' % value)

    def getValue(self):
        return float(self.text().replace(',', '.'))


class Detector(MeasElement, QComboBox):

    CACHE_KEY = 'detector/presets'
    LABEL = 'Detector'

    changed = pyqtSignal(object)

    def init(self, ename, client, value=None):
        MeasElement.init(self, ename, client, value)
        self.allvalues = client.getDeviceParam(*self.CACHE_KEY.split('/'))
        self.currentIndexChanged.connect(self._changed)
        self.pvalue = value

    def othersChanged(self, ename, value):
        if ename == 'selector' and self.allvalues is not None:
            values = self.allvalues[value]
            prev = self.currentText() or self.pvalue
            self.clear()
            self.addItems(list(values))
            index = self.findText(prev)
            if index >= 0:
                self.setCurrentIndex(index)

    def getValue(self):
        return self.currentText()


class Chopper(MeasElement, QComboBox):

    CACHE_KEY = 'chopper/resolutions'
    LABEL = u'TOF dλ/λ'

    changed = pyqtSignal(object)

    def init(self, ename, client, value=None):
        MeasElement.init(self, ename, client, value)
        resos = client.getDeviceParam(*self.CACHE_KEY.split('/'))
        values = ['off'] + ['%.1f%%' % v for v in resos]
        self.addItems(values)
        if value is not None and value in values:
            self.setCurrentIndex(values.index(value))
        self.currentIndexChanged.connect(self._changed)
        self.pvalue = value

    def getValue(self):
        return self.currentText()


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


class MeasTime(FloatElement):
    LABEL = 'Time'
