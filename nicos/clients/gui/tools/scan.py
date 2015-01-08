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

"""Graphical interface to prepare scan commands."""

from PyQt4.QtGui import QDialog, QDoubleValidator, QIntValidator, QButtonGroup
from PyQt4.QtCore import SIGNAL

from nicos.clients.gui.utils import loadUi, DlgPresets

def toint(text):
    text = str(text)
    if not text:
        return 0
    return int(text)

def tofloat(text):
    text = str(text)
    if not text:
        return 0.0
    return float(text)

def fmt_time(seconds):
    if seconds < 60:
        return '%d sec' % seconds
    elif seconds < 3600:
        return '%d min' % (seconds / 60)
    else:
        return '%d h %d min' % (seconds / 3600, (seconds % 3600) / 60)


class ScanTool(QDialog):
    def __init__(self, parent, client, **settings):
        QDialog.__init__(self, parent)
        loadUi(self, 'scan.ui', 'tools')

        self.scanButtonGroup = QButtonGroup()
        self.scanButtonGroup.addButton(self.scanSingle)
        self.scanButtonGroup.addButton(self.scanCentered)
        self.qscanButtonGroup = QButtonGroup()
        self.qscanButtonGroup.addButton(self.qscanSingle)
        self.qscanButtonGroup.addButton(self.qscanCentered)
        self.qscanButtonGroup.addButton(self.qscanRandom)
        self.qscanButtonGroup.addButton(self.qscanLong)
        self.qscanButtonGroup.addButton(self.qscanTrans)
        self.presetButtonGroup = QButtonGroup()
        self.presetButtonGroup.addButton(self.presetTime)
        self.presetButtonGroup.addButton(self.presetMonitor)

        self.connect(self.scanButtonGroup, SIGNAL('buttonClicked(int)'), self.updateCommand)
        self.connect(self.qscanButtonGroup, SIGNAL('buttonClicked(int)'), self.updateCommand)
        self.connect(self.presetButtonGroup, SIGNAL('buttonClicked(int)'), self.updateCommand)
        self.connect(self.stepsInput, SIGNAL('valueChanged(int)'), self.updateCommand)
        self.connect(self.timeInput, SIGNAL('valueChanged(int)'), self.updateCommand)
        self.connect(self.monitorInput, SIGNAL('valueChanged(int)'), self.updateCommand)

        self.connect(self.deviceList, SIGNAL('itemSelectionChanged ()'), self.updateCommand)

        self.connect(self.scanPreset, SIGNAL('textChanged(QString)'), self.updateCommand)
        self.connect(self.scanNumsteps, SIGNAL('textChanged(QString)'), self.updateCommand)
        self.connect(self.scanStep, SIGNAL('textChanged(QString)'), self.updateCommand)
        self.connect(self.scanStart, SIGNAL('textChanged(QString)'), self.updateCommand)
        self.connect(self.deviceName, SIGNAL('textChanged(QString)'), self.updateCommand)
        self.connect(self.scanRange, SIGNAL('textChanged(QString)'), self.updateCommand)

        self.connect(self.hInput, SIGNAL('textChanged(QString)'), self.updateCommand)
        self.connect(self.kInput, SIGNAL('textChanged(QString)'), self.updateCommand)
        self.connect(self.lInput, SIGNAL('textChanged(QString)'), self.updateCommand)
        self.connect(self.EInput, SIGNAL('textChanged(QString)'), self.updateCommand)
        self.connect(self.deltahInput, SIGNAL('textChanged(QString)'), self.updateCommand)
        self.connect(self.deltakInput, SIGNAL('textChanged(QString)'), self.updateCommand)
        self.connect(self.deltalInput, SIGNAL('textChanged(QString)'), self.updateCommand)
        self.connect(self.deltaEInput, SIGNAL('textChanged(QString)'), self.updateCommand)
        self.connect(self.deltaqInput, SIGNAL('textChanged(QString)'), self.updateCommand)

        self.connect(self.generateBtn, SIGNAL('clicked()'), self.createCommand)
        self.connect(self.clearAllBtn, SIGNAL('clicked()'), self.clearAll)
        self.connect(self.quitBtn, SIGNAL('clicked()'), self.close)
        self.connect(self.scanCalc, SIGNAL('clicked()'), self.calc_scan)
        self.connect(self.qscanCalc, SIGNAL('clicked()'), self.calc_qscan)

        self.connect(self.qscanSingle, SIGNAL('clicked()'), self.set_qlabels)
        self.connect(self.qscanCentered, SIGNAL('clicked()'), self.set_qlabels)
        self.connect(self.qscanLong, SIGNAL('clicked()'), self.set_qlabels)
        self.connect(self.qscanTrans, SIGNAL('clicked()'), self.set_qlabels)
        self.connect(self.qscanRandom, SIGNAL('clicked()'), self.set_qlabels)

        self._devices = sorted(parent.client.eval(
            '[(dev.name, dev.unit) '
            'for (name, dev) in session.devices.items() '
            'if name in session.explicit_devices and hasattr(dev, "maw")]',
            []))

        self.tabWidget.setTabEnabled(0, self._devices != [])
        for name, unit in self._devices:
            self.deviceList.addItem("%s [%s]" % (name, unit))

        dval = QDoubleValidator(self)
        ival = QIntValidator(self)

        # qscan tab
        self.hInput.setValidator(dval)
        self.kInput.setValidator(dval)
        self.lInput.setValidator(dval)
        self.EInput.setValidator(dval)
        self.deltahInput.setValidator(dval)
        self.deltakInput.setValidator(dval)
        self.deltalInput.setValidator(dval)
        self.deltaEInput.setValidator(dval)
        self.deltaqInput.setValidator(dval)

        # disabled for now
        self.qscanRandom.setVisible(False)
        self.qscanTrans.setVisible(False)
        self.qscanLong.setVisible(False)

        # scan/cscan tab
        self.scanStart.setValidator(dval)
        self.scanStep.setValidator(dval)
        self.scanNumsteps.setValidator(ival)
        self.scanPreset.setValidator(dval)
        self.scanMovetime.setValidator(dval)

        self.presets = DlgPresets('scaninput', [
            # qscan tab
            (self.qscanSingle, 1), (self.qscanCentered, 0),
            (self.qscanLong, 0), (self.qscanTrans, 0),
            (self.qscanRandom, 0), (self.monitorInput, 10000),
            (self.timeInput, 120), (self.presetTime, 1),
            (self.presetMonitor, 0),
            (self.hInput, '0.0'), (self.kInput, '0.0'),
            (self.lInput, '0.0'), (self.EInput, '0.0'),
            (self.deltahInput, '0.0'), (self.deltakInput, '0.0'),
            (self.deltalInput, '0.0'), (self.deltaEInput, '0.0'),
            (self.deltaqInput, '0.0'), (self.stepsInput, 10),
            # scan tab
            (self.scanSingle, 1), (self.scanCentered, 0),
            (self.scanStart, '0.0'), (self.scanStep, '0.0'),
            (self.scanNumsteps, '0'), (self.scanPreset, '0.0'),
            (self.deviceList, 'om [deg]'), (self.deviceName, ''),
            (self.scanMovetime, '0'),
            # the tab itself
            (self.tabWidget, 0),
        ])
        self.presets.load()
        self.set_qlabels()

    def set_qlabels(self, *args):
        if self.qscanCentered.isChecked() or self.qscanSingle.isChecked():
            self.label_dh.setText(u'<b>∆h</b>')
            self.label_dk.setText(u'<b>∆k</b>')
            self.label_dl.setText(u'<b>∆l</b>')
            self.deltahInput.setEnabled(True)
            self.deltakInput.setEnabled(True)
            self.deltalInput.setEnabled(True)
            self.deltaqInput.setEnabled(False)
        elif self.qscanLong.isChecked() or self.qscanTrans.isChecked():
            self.label_dh.setText('')
            self.label_dk.setText('')
            self.label_dl.setText('')
            self.deltahInput.setEnabled(False)
            self.deltakInput.setEnabled(False)
            self.deltalInput.setEnabled(False)
            self.deltaqInput.setEnabled(True)
        elif self.qscanRandom.isChecked():
            self.label_dh.setText(u'<b>u</b>')
            self.label_dk.setText(u'<b>v</b>')
            self.label_dl.setText(u'<b>w</b>')
            self.deltahInput.setEnabled(True)
            self.deltakInput.setEnabled(True)
            self.deltalInput.setEnabled(True)
            self.deltaqInput.setEnabled(True)

    def close(self, *args):
        """Close the window and save the settings."""
        self.presets.save()
        return True

    def closeEvent(self, event):
        self.presets.save()
        self.deleteLater()
        self.accept()

    def clearAll(self):
        # Clear scan
        self.scanStart.clear()
        self.scanStep.clear()
        self.scanNumsteps.clear()
        self.scanPreset.clear()
        self.scanRange.clear()
        self.scanEstimation.clear()
        self.scanMovetime.clear()
        # Clear qscan
        self.hInput.clear()
        self.deltahInput.clear()
        self.kInput.clear()
        self.deltakInput.clear()
        self.lInput.clear()
        self.deltalInput.clear()
        self.EInput.clear()
        self.deltaEInput.clear()
        self.deltaqInput.clear()

    def calc_scan(self):
        stepsize = tofloat(self.scanStep.text())
        numstep = toint(self.scanNumsteps.text())
        startpos = tofloat(self.scanStart.text())
        movetime = tofloat(self.scanMovetime.text())
        preset = tofloat(self.scanPreset.text())

        if self.scanSingle.isChecked():
            endpos = startpos + (stepsize - 1) * numstep
            self.scanRange.setText('- %.2f' % endpos)
            seconds = (movetime + preset) * numstep
        else:
            lowerend = startpos - stepsize * numstep
            upperend = startpos + stepsize * numstep
            self.scanRange.setText('%.2f - %.2f' % (lowerend, upperend))
            seconds = (movetime + preset) * (2 * numstep + 1)

        self.scanEstimation.setText(fmt_time(seconds))
        return seconds

    def calc_qscan(self):
        numstep = toint(self.stepsInput.text())
        if self.qscanCentered.isChecked() or self.qscanLong.isChecked() or \
               self.qscanTrans.isChecked():
            numstep = 2 * numstep + 1
        if self.presetTime.isChecked():
            preset = tofloat(self.timeInput.text())
            seconds = numstep * preset
            self.qscanEstimation.setText(fmt_time(seconds))
            return seconds
        else:
            self.qscanEstimation.setText('no estimation possible')
            return 0

    def updateCommand(self):
        self.cmdResult.setText(u'<b>%s</b>' % self._getCommand())

    def _getCommand(self):
        tab = self.tabWidget.currentIndex()

        def timeest(secs):
            if secs == 0:
                return ''
            return '#- %d sec (%s)\n' % (secs, fmt_time(secs))

        # Qscan
        if tab == 1:
            params = [
                ('h', self.hInput, tofloat),
                ('k', self.kInput, tofloat),
                ('l', self.lInput, tofloat),
                ('E', self.EInput, tofloat),
                ('n', self.stepsInput, toint),
                ('dh', self.deltahInput, tofloat),
                ('dk', self.deltakInput, tofloat),
                ('dl', self.deltalInput, tofloat),
                ('dE', self.deltaEInput, tofloat),
                ('dq', self.deltaqInput, tofloat),
                ('t', self.timeInput, tofloat),
                ('m', self.monitorInput, toint),
            ]
            d = dict((name, func(ctl.text())) for (name, ctl, func) in params)

            if self.qscanSingle.isChecked():
                cmdname = 'qscan'
            elif self:
                cmdname = 'qcscan'
            else:
                return  # for now

            scan = cmdname + '([%(h)s, %(k)s, %(l)s, %(E)s], ' \
                '[%(dh)s, %(dk)s, %(dl)s, %(dE)s], %(n)s' % d

            if self.presetTime.isChecked():
                scan += ', t=%s)' % d['t']
            else:
                scan += ', m1=%s)' % d['m']

            cmd = timeest(self.calc_qscan())
            cmd += scan

        # scan
        else:
            devname = self.deviceName.text()
            if not devname:
                devname = self._devices[self.deviceList.currentRow()][0]

            if self.scanCentered.isChecked():
                cmdname = 'cscan'
            else:
                cmdname = 'scan'

            params = [devname]
            for (_pn, ctl, fn) in (('start', self.scanStart, tofloat),
                                   ('step', self.scanStep, tofloat),
                                   ('numsteps', self.scanNumsteps, toint),
                                   ('preset', self.scanPreset, tofloat)):
                val = fn(ctl.text())
                params.append(str(val))

            cmd = timeest(self.calc_scan())
            cmd += '%s(%s)' % (cmdname, ', '.join(params))
        return cmd + '\n'

    def createCommand(self):
        self.emit(SIGNAL('addCode'), self._getCommand())
