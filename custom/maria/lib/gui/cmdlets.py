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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS GUI cmdlets for MARIA."""

from os import path

from PyQt4.QtCore import SIGNAL

from nicos.clients.gui.cmdlets import Cmdlet, register, isFloat
from nicos.guisupport.utils import DoubleValidator
from nicos.utils import findResource, formatDuration


customgui = path.join("custom", "maria", "lib", "gui")


class SScan(Cmdlet):

    name = "Step Scan (start, step, end)"
    category = "Scan"

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client,
                        findResource(path.join(customgui, "sscan.ui")))
        self.device.addItems(
            self.client.getDeviceList("nicos.core.device.Moveable"))
        self.on_device_change(self.device.currentText())
        self.connect(self.device, SIGNAL("currentIndexChanged(const QString&)"),
                     self.on_device_change)
        self.start.setValidator(DoubleValidator(self))
        self.stop.setValidator(DoubleValidator(self))
        self.step.setValidator(DoubleValidator(self))
        self.delta.setValidator(DoubleValidator(self))
        self.start.textChanged.connect(self.on_range_change)
        self.stop.textChanged.connect(self.on_range_change)
        self.step.textChanged.connect(self.on_range_change)
        self.delta.textChanged.connect(self.on_range_change)

    def on_range_change(self):
        try:
            start = float(self.start.text())
            end = float(self.stop.text())
            step = float(self.step.text())
            counttime = float(self.delta.text())
            numpoints = int(round((end - start) / step + 1))
            secs = numpoints * counttime
            self.totalLabel.setText("Total: %d points, %s" %
                                    (numpoints, formatDuration(secs)))
        except (ValueError, ArithmeticError):
            self.totalLabel.setText("Total:")
        self.changed()

    def on_device_change(self, text):
        unit = self.client.getDeviceParam(text, "unit")
        value = self.client.getDeviceParam(text, "value")
        fmtstr = self.client.getDeviceParam(text, "fmtstr")
        try:
            self.start.setText(fmtstr % value)
        except Exception:
            pass
        self.unit1.setText(unit or "")
        self.unit2.setText(unit or "")
        self.unit3.setText(unit or "")
        self.changed()

    def getValues(self):
        return {"dev": self.device.currentText(),
                "scanstart": self.start.text(),
                "scanend": self.stop.text(),
                "scanstep": self.step.text(),
                "counttime": float(self.delta.text())}

    def setValues(self, values):
        self._setDevice(values)
        if "scanstart" in values:
            self.start.setText(values["scanstart"])
        if "scanend" in values:
            self.stop.setText(values["scanend"])
        if "scanstep" in values:
            self.step.setText(values["scanstep"])
        if "counttime" in values:
            self.delta.setText(str(values["counttime"]))

    def isValid(self):
        valid = [
            self.markValid(self.start, isFloat(self.start)),
            self.markValid(self.stop, isFloat(self.stop)),
            self.markValid(self.step, isFloat(self.step)),
            self.markValid(self.delta, isFloat(self.delta, 0.05)),
        ]
        return all(valid)

    def generate(self, mode):
        if mode == "simple":
            return "sscan %(dev)s %(scanstart)s %(scanstep)s %(scanend)s " \
                   "%(counttime)s" % self.getValues()
        return "sscan(%(dev)s, %(scanstart)s, %(scanstep)s, %(scanend)s, " \
               "%(counttime)s)" % self.getValues()


class KScan(Cmdlet):

    name = 'Kinematic Scan'
    category = 'Scan'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client,
                        findResource(path.join(customgui, "kscan.ui")))
        self.device.addItems(
            self.client.getDeviceList('nicos.core.device.Moveable',
                                      special_clause='hasattr(d, "speed")'))
        self.on_device_change(self.device.currentText())
        self.connect(self.device, SIGNAL('currentIndexChanged(const QString&)'),
                     self.on_device_change)
        self.start.setValidator(DoubleValidator(self))
        self.step.setValidator(DoubleValidator(self))
        self.speed.setValidator(DoubleValidator(self))
        self.start.textChanged.connect(self.on_range_change)
        self.step.textChanged.connect(self.on_range_change)
        self.speed.textChanged.connect(self.on_range_change)
        self.numpoints.valueChanged.connect(self.on_range_change)

    def on_range_change(self):
        try:
            pnts = self.numpoints.value()
            rng = abs(float(self.step.text()))
            secs = pnts * rng / float(self.speed.text())
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
                'scanstep': self.step.text(),
                'scanpoints': self.numpoints.value(),
                'devspeed': self.speed.text()}

    def setValues(self, values):
        self._setDevice(values)
        if 'scanstart' in values:
            self.start.setText(values['scanstart'])
        if 'scanstep' in values:
            self.step.setText(values['scanstep'])
        if 'scanpoints' in values:
            self.numpoints.setValue(values['scanpoints'])
        if 'devspeed' in values:
            self.speed.setText(values['devspeed'])

    def isValid(self):
        valid = [
            self.markValid(self.start, isFloat(self.start)),
            self.markValid(self.step, isFloat(self.step)),
            self.markValid(self.speed, isFloat(self.speed, 0.00001)),
            self.markValid(self.numpoints, self.numpoints.value() >= 2),
        ]
        return all(valid)

    def generate(self, mode):
        if mode == 'simple':
            return 'kscan %(dev)s %(scanstart)s %(scanstep)s %(scanpoints)s ' \
                   '%(devspeed)s' % self.getValues()
        return 'kscan(%(dev)s, %(scanstart)s, %(scanstep)s, %(scanpoints)s, ' \
               '%(devspeed)s)' % self.getValues()


register(KScan)
register(SScan)
