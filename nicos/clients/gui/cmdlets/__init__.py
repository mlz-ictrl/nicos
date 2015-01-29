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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI command input widgets."""

from PyQt4.QtGui import QWidget, QColor
from PyQt4.QtCore import Qt, pyqtSignal, SIGNAL

from nicos.utils import formatDuration
from nicos.guisupport.typedvalue import DeviceValueEdit, DeviceParamEdit
from nicos.clients.gui.utils import loadUi, setBackgroundColor

invalid = QColor('#ffcccc')


def isFloat(ctl, minval=None, maxval=None):
    try:
        v = float(ctl.text())
    except ValueError:
        return False
    if minval is not None and v < minval:
        return False
    if maxval is not None and v > maxval:
        return False
    return True


class Cmdlet(QWidget):

    name = ''
    category = ''

    cmdletUp = pyqtSignal()
    cmdletDown = pyqtSignal()
    cmdletRemove = pyqtSignal()

    def __init__(self, parent, client, uifile):
        self.client = client
        QWidget.__init__(self, parent)
        loadUi(self, uifile, 'cmdlets')
        loadUi(self.buttons, 'buttons.ui', 'cmdlets')
        self.buttons.upBtn.clicked.connect(self.cmdletUp)
        self.buttons.downBtn.clicked.connect(self.cmdletDown)
        self.buttons.delBtn.clicked.connect(self.cmdletRemove)

    def removeSelf(self):
        self.parent().layout().removeWidget(self)
        self.hide()

    def changed(self, *args):
        """Should be emitted whenever any value in the cmdlet changes."""
        self.emit(SIGNAL('dataChanged'))

    def markValid(self, ctl, condition):
        if condition:
            setBackgroundColor(ctl, Qt.white)
        else:
            setBackgroundColor(ctl, invalid)
        return condition

    def isValid(self):
        """Check if all entered data is valid.

        This method can change widget styles to indicate invalid data with
        the markValid() method if wanted.
        """
        return True

    def generate(self, mode):
        """Generate code for the commandlet.

        *mode* is 'python' or 'simple'.

        Should generate a string of lines, complete with newlines.
        """
        return ''


class Move(Cmdlet):

    name = 'Move'
    category = 'Device'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client, 'move.ui')
        self.target = DeviceValueEdit(self)
        self.target.setClient(self.client)
        self.connect(self.target, SIGNAL('dataChanged'), self.changed)
        self.hlayout.insertWidget(3, self.target)
        self.device.addItems(self.client.getDeviceList('nicos.core.device.Moveable'))
        self.on_device_change(self.device.currentText())
        self.connect(self.device, SIGNAL('currentIndexChanged(const QString&)'),
                     self.on_device_change)
        self.waitBox.stateChanged.connect(self.changed)

    def on_device_change(self, text):
        self.target.dev = text
        self.changed()

    def isValid(self):
        return self.markValid(self.target, True)

    def generate(self, mode):
        cmd = 'maw'
        if not self.waitBox.isChecked():
            cmd = 'move'
        args = (cmd, self.device.currentText(), self.target.getValue())
        if mode == 'simple':
            return '%s %s %r\n' % args
        return '%s(%s, %r)\n' % args


class Count(Cmdlet):

    name = 'Count'
    category = 'Scan'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client, 'count.ui')
        self.seconds.valueChanged.connect(self.changed)

    def isValid(self):
        return self.markValid(self.seconds, self.seconds.value() > 0)

    def generate(self, mode):
        if mode == 'simple':
            return 'count %s\n' % self.seconds.value()
        return 'count(%s)\n' % self.seconds.value()


class Scan(Cmdlet):

    name = 'Scan'
    category = 'Scan'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client, 'scan.ui')
        self.device.addItems(self.client.getDeviceList('nicos.core.device.Moveable'))
        self.on_device_change(self.device.currentText())
        self.connect(self.device, SIGNAL('currentIndexChanged(const QString&)'),
                     self.on_device_change)
        self.start.textChanged.connect(self.on_range_change)
        self.step.textChanged.connect(self.on_range_change)
        self.numpoints.valueChanged.connect(self.on_range_change)
        self.seconds.valueChanged.connect(self.changed)

    def on_device_change(self, text):
        unit = self.client.getDeviceParam(text, 'unit')
        self.unit1.setText(unit or '')
        self.unit2.setText(unit or '')
        self.changed()

    def on_range_change(self, *args):
        try:
            start = float(self.start.text())
            step = float(self.step.text())
        except ValueError:
            endpos = ''
        else:
            numpoints = self.numpoints.value()
            endpos = '%.3f %s' % (start + (numpoints-1)*step, self.unit1.text())
        self.endPos.setText(endpos)
        self.changed()

    def isValid(self):
        # NOTE: cannot use "return markValid() and markValid() and ..." because
        # that short-circuits evaluation and therefore skips marking all but the
        # first invalid control
        valid = [
            self.markValid(self.start, self.start.text()),
            self.markValid(self.step, self.step.text()),
            self.markValid(self.seconds, self.seconds.value() > 0),
        ]
        return all(valid)

    def generate(self, mode):
        args = (
            self.device.currentText(),
            self.start.text(),
            self.step.text(),
            self.numpoints.value(),
            self.seconds.value(),
        )
        if mode == 'simple':
            return 'scan %s %s %s %s %s\n' % args
        return 'scan(%s, %s, %s, %s, %s)\n' % args


class CScan(Cmdlet):

    name = 'Centered Scan'
    category = 'Scan'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client, 'cscan.ui')
        self.device.addItems(self.client.getDeviceList('nicos.core.device.Moveable'))
        self.on_device_change(self.device.currentText())
        self.connect(self.device, SIGNAL('currentIndexChanged(const QString&)'),
                     self.on_device_change)
        self.start.textChanged.connect(self.on_range_change)
        self.step.textChanged.connect(self.on_range_change)
        self.numpoints.valueChanged.connect(self.on_range_change)
        self.seconds.valueChanged.connect(self.changed)

    def on_device_change(self, text):
        unit = self.client.getDeviceParam(text, 'unit')
        self.unit1.setText(unit or '')
        self.unit2.setText(unit or '')
        self.changed()

    def on_range_change(self, *args):
        numpoints = self.numpoints.value()
        try:
            start = float(self.start.text())
            step = float(self.step.text())
        except ValueError:
            edgepos = ''
        else:
            edgepos = '%.3f - %.3f %s' % (start - numpoints*step,
                                          start + numpoints*step,
                                          self.unit1.text())
        self.edgePos.setText(edgepos)
        self.totalPoints.setText('Total: %d points' % (2 * numpoints + 1))
        self.changed()

    def isValid(self):
        valid = [
            self.markValid(self.start, self.start.text()),
            self.markValid(self.step, self.step.text()),
            self.markValid(self.seconds, self.seconds.value() > 0),
        ]
        return all(valid)

    def generate(self, mode):
        args = (
            self.device.currentText(),
            self.start.text(),
            self.step.text(),
            self.numpoints.value(),
            self.seconds.value(),
        )
        if mode == 'simple':
            return 'cscan %s %s %s %s %s\n' % args
        return 'cscan(%s, %s, %s, %s, %s)\n' % args


class ContScan(Cmdlet):

    name = 'Continuous Scan'
    category = 'Scan'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client, 'contscan.ui')
        self.device.addItems(
            self.client.getDeviceList('nicos.core.device.Moveable',
                                      special_clause='hasattr(d, "speed")'))
        self.on_device_change(self.device.currentText())
        self.connect(self.device, SIGNAL('currentIndexChanged(const QString&)'),
                     self.on_device_change)
        self.start.textChanged.connect(self.on_range_change)
        self.stop.textChanged.connect(self.on_range_change)
        self.speed.textChanged.connect(self.on_range_change)
        self.delta.textChanged.connect(self.on_range_change)

    def on_range_change(self):
        try:
            rng = abs(float(self.start.text()) - float(self.stop.text()))
            secs = rng / float(self.speed.text())
            pnts = int(secs / float(self.delta.text()))
            self.totalLabel.setText('Total: %d points, %s' %
                                    (pnts, formatDuration(secs)))
        except (ValueError, ArithmeticError):
            self.totalLabel.setText('Total:')
        self.changed()

    def on_device_change(self, text):
        unit = self.client.getDeviceParam(text, 'unit')
        value = self.client.getDeviceParam(text, 'value')
        fmtstr = self.client.getDeviceParam(text, 'fmtstr')
        try:
            self.start.setText(fmtstr % value)
        except Exception:
            pass
        self.unit1.setText(unit or '')
        self.unit2.setText(unit or '')
        self.unit3.setText((unit or '') + '/second')
        self.changed()

    def isValid(self):
        valid = [
            self.markValid(self.start, isFloat(self.start)),
            self.markValid(self.stop, isFloat(self.stop)),
            self.markValid(self.speed, isFloat(self.speed, 0.00001)),
            self.markValid(self.delta, isFloat(self.delta, 0.05)),
        ]
        return all(valid)

    def generate(self, mode):
        args = (
            self.device.currentText(),
            self.start.text(),
            self.stop.text(),
            self.speed.text(),
            self.delta.text(),
        )
        if mode == 'simple':
            return 'contscan %s %s %s %s %s\n' % args
        return 'contscan(%s, %s, %s, %s, %s)\n' % args


class Sleep(Cmdlet):

    name = 'Sleep'
    category = 'Other'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client, 'sleep.ui')
        self.seconds.valueChanged.connect(self.changed)

    def isValid(self):
        return self.markValid(self.seconds, self.seconds.value() > 0)

    def generate(self, mode):
        if mode == 'simple':
            return 'sleep %s\n' % self.seconds.text()
        return 'sleep(%s)\n' % self.seconds.text()


class Configure(Cmdlet):

    name = 'Configure'
    category = 'Device'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client, 'configure.ui')
        self.paraminfo = {}
        self.paramvalues = {}
        self.target = DeviceParamEdit(self)
        self.target.setClient(self.client)
        self.connect(self.target, SIGNAL('dataChanged'), self.changed)
        self.hlayout.insertWidget(5, self.target)
        self.device.addItems(self.client.getDeviceList())
        self.on_device_change(self.device.currentText())
        self.connect(self.device, SIGNAL('currentIndexChanged(const QString&)'),
                     self.on_device_change)
        self.connect(self.parameter, SIGNAL('currentIndexChanged(const QString&)'),
                     self.on_parameter_change)

    def on_device_change(self, text):
        self.paraminfo = self.client.getDeviceParamInfo(text)
        self.paramvalues = dict(self.client.getDeviceParams(text))
        self.parameter.clear()
        self.parameter.addItems(sorted(p for p in self.paraminfo
                                       if self.paraminfo[p]['settable'] and
                                          self.paraminfo[p]['userparam']))
        self.target.dev = text
        self.on_parameter_change(self.parameter.currentText())
        self.changed()

    def on_parameter_change(self, text):
        self.target.param = text
        self.changed()

    def isValid(self):
        return self.markValid(self.target, True)

    def generate(self, mode):
        args = (self.device.currentText(), self.parameter.currentText(),
                self.target.getValue())
        if mode == 'simple':
            return 'set %s %s %r\n' % args
        return '%s.%s = %r\n' % args


class NewSample(Cmdlet):

    name = 'New sample'
    category = 'Other'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client, 'sample.ui')
        self.samplename.textChanged.connect(self.changed)

    def generate(self, mode):
        if mode == 'simple':
            return 'NewSample %r\n' % self.samplename.text()
        return 'NewSample(%r)\n' % self.samplename.text()


all_cmdlets = [Move, Count, Scan, CScan, ContScan, Sleep, Configure, NewSample]
all_categories = ['Device', 'Scan', 'Other']
