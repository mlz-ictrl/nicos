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

from PyQt4.QtGui import QWidget, QColor, QDoubleValidator
from PyQt4.QtCore import Qt, pyqtSignal, SIGNAL

from nicos.utils import formatDuration
from nicos.guisupport.typedvalue import DeviceValueEdit, DeviceParamEdit
from nicos.guisupport.utils import setBackgroundColor
from nicos.clients.gui.utils import loadUi

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
        """Should be called whenever any value in the cmdlet changes."""
        self.emit(SIGNAL('dataChanged'))

    def getValues(self):
        """Return a dict with the values of the cmdlet.

        Values should have a name that is the same for the same logical
        value in multiple cmdlets, e.g. "dev" for the device in a command.
        """
        return {}

    def _setDevice(self, values):
        """Helper for setValues for setting a device combo box."""
        if 'dev' in values:
            idx = self.device.findText(values['dev'])
            if idx > -1:
                self.device.setCurrentIndex(idx)

    def setValues(self, values):
        """Set values of the cmdlet with values from the argument.

        Unknown values must be ignored.
        """

    def markValid(self, ctl, condition):
        """Return boolean condition, and also mark the offending widget.

        For use in isValid().
        """
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

    def getValues(self):
        return {'dev':    self.device.currentText(),
                'moveto': self.target.getValue()}

    def setValues(self, values):
        self._setDevice(values)
        # DeviceValueEdit doesn't support setValue (yet)
        # if 'moveto' in values:
        #     self.target.setValue(values['moveto'])

    def isValid(self):
        return self.markValid(self.target, True)

    def generate(self, mode):
        cmd = 'maw' if self.waitBox.isChecked() else 'move'
        if mode == 'simple':
            return cmd + ' %(dev)s %(moveto)r' % self.getValues()
        return cmd + '(%(dev)s, %(moveto)r)' % self.getValues()


class Count(Cmdlet):

    name = 'Count'
    category = 'Scan'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client, 'count.ui')
        self.seconds.valueChanged.connect(self.changed)

    def getValues(self):
        return {'counttime': self.seconds.value()}

    def setValues(self, values):
        if 'counttime' in values:
            self.seconds.setValue(values['counttime'])

    def isValid(self):
        return self.markValid(self.seconds, self.seconds.value() > 0)

    def generate(self, mode):
        if mode == 'simple':
            return 'count %(counttime)s' % self.getValues()
        return 'count(%(counttime)s)' % self.getValues()


class CommonScan(Cmdlet):

    cmdname = ''
    uiname = ''

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client, self.uiname)
        self.device.addItems(self.client.getDeviceList('nicos.core.device.Moveable'))
        self.on_device_change(self.device.currentText())
        self.connect(self.device, SIGNAL('currentIndexChanged(const QString&)'),
                     self.on_device_change)
        self.start.setValidator(QDoubleValidator(self))
        self.step.setValidator(QDoubleValidator(self))
        self.start.textChanged.connect(self.on_range_change)
        self.step.textChanged.connect(self.on_range_change)
        self.numpoints.valueChanged.connect(self.on_range_change)
        self.seconds.valueChanged.connect(self.changed)

    def on_device_change(self, text):
        unit = self.client.getDeviceParam(text, 'unit')
        self.unit1.setText(unit or '')
        self.unit2.setText(unit or '')
        self.changed()

    def getValues(self):
        return {'dev': self.device.currentText(),
                'scanstart': self.start.text(),
                'scanstep': self.step.text(),
                'scanpoints': self.numpoints.value(),
                'counttime': self.seconds.value()}

    def setValues(self, values):
        self._setDevice(values)
        if 'scanstart' in values:
            self.start.setText(values['scanstart'])
        if 'scanstep' in values:
            self.step.setText(values['scanstep'])
        if 'scanpoints' in values:
            self.numpoints.setValue(values['scanpoints'])
        if 'counttime' in values:
            self.seconds.setValue(int(values['counttime']))

    def isValid(self):
        # NOTE: cannot use "return markValid() and markValid() and ..." because
        # that short-circuits evaluation and therefore skips marking all but the
        # first invalid control
        valid = [
            self.markValid(self.start, isFloat(self.start)),
            self.markValid(self.step, isFloat(self.step)),
            self.markValid(self.seconds, self.seconds.value() > 0),
        ]
        return all(valid)

    def generate(self, mode):
        if mode == 'simple':
            return self.cmdname + ' %(dev)s %(scanstart)s %(scanstep)s ' \
                '%(scanpoints)s %(counttime)s' % self.getValues()
        return self.cmdname + '(%(dev)s, %(scanstart)s, %(scanstep)s, ' \
            '%(scanpoints)s, %(counttime)s)' % self.getValues()


class Scan(CommonScan):

    name = 'Scan'
    category = 'Scan'
    cmdname = 'scan'
    uiname = 'scan.ui'

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


class CScan(CommonScan):

    name = 'Centered Scan'
    category = 'Scan'
    cmdname = 'cscan'
    uiname = 'cscan.ui'

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
        self.start.setValidator(QDoubleValidator(self))
        self.stop.setValidator(QDoubleValidator(self))
        self.speed.setValidator(QDoubleValidator(self))
        self.delta.setValidator(QDoubleValidator(self))
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

    def getValues(self):
        return {'dev': self.device.currentText(),
                'scanstart': self.start.text(),
                'scanend': self.stop.text(),
                'devspeed': self.speed.text(),
                'counttime': float(self.delta.text())}

    def setValues(self, values):
        self._setDevice(values)
        if 'scanstart' in values:
            self.start.setText(values['scanstart'])
        if 'scanend' in values:
            self.stop.setText(values['scanend'])
        if 'devspeed' in values:
            self.speed.setText(values['devspeed'])
        if 'counttime' in values:
            self.delta.setText(str(values['counttime']))

    def isValid(self):
        valid = [
            self.markValid(self.start, isFloat(self.start)),
            self.markValid(self.stop, isFloat(self.stop)),
            self.markValid(self.speed, isFloat(self.speed, 0.00001)),
            self.markValid(self.delta, isFloat(self.delta, 0.05)),
        ]
        return all(valid)

    def generate(self, mode):
        if mode == 'simple':
            return 'contscan %(dev)s %(scanstart)s %(scanend)s %(devspeed)s ' \
                   '%(counttime)s' % self.getValues()
        return 'contscan(%(dev)s, %(scanstart)s, %(scanend)s, %(devspeed)s, ' \
               '%(counttime)s)' % self.getValues()


class Sleep(Cmdlet):

    name = 'Sleep'
    category = 'Other'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client, 'sleep.ui')
        self.seconds.valueChanged.connect(self.changed)

    def getValues(self):
        return {'sleeptime': self.seconds.value()}

    def setValues(self, values):
        if 'sleeptime' in values:
            self.seconds.setValue(values['sleeptime'])

    def isValid(self):
        return self.markValid(self.seconds, self.seconds.value() > 0)

    def generate(self, mode):
        if mode == 'simple':
            return 'sleep %(sleeptime)s' % self.getValues()
        return 'sleep(%(sleeptime)s)' % self.getValues()


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

    def getValues(self):
        return {'dev': self.device.currentText(),
                'param': self.parameter.currentText(),
                'paramvalue': self.target.getValue()}

    def setValues(self, values):
        self._setDevice(values)
        if 'param' in values:
            idx = self.parameter.findText(values['param'])
            if idx > -1:
                self.parameter.setCurrentIndex(idx)
        # DeviceValueEdit doesn't support setValue (yet)
        # if 'paramvalue' in values:
        #     self.target.setValue(values['paramvalue'])

    def isValid(self):
        return self.markValid(self.target, True)

    def generate(self, mode):
        if mode == 'simple':
            return 'set %(dev)s %(param)s %(paramvalue)r' % self.getValues()
        return 'set(%(dev)s, %(param)r, %(paramvalue)r)' % self.getValues()


class NewSample(Cmdlet):

    name = 'New sample'
    category = 'Other'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client, 'sample.ui')
        self.samplename.textChanged.connect(self.changed)

    def getValues(self):
        return {'samplename': self.samplename.text()}

    def setValues(self, values):
        if 'samplename' in values:
            self.samplename.setText(values['samplename'])

    def generate(self, mode):
        if mode == 'simple':
            return 'NewSample %(samplename)r' % self.getValues()
        return 'NewSample(%(samplename)r)' % self.getValues()


all_cmdlets = [Move, Count, Scan, CScan, ContScan, Sleep, Configure, NewSample]
all_categories = ['Device', 'Scan', 'Other']
