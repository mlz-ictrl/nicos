#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

__version__ = "$Revision$"

from os import path

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QDialog, QDoubleValidator, QIntValidator
from PyQt4.uic import loadUi

from nicos.gui.tools.uitools import DlgPresets, runDlgStandalone

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


class ScanInputDlg(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        loadUi(path.join(path.dirname(__file__), 'scan.ui'), self)

        self.connect(self.pB_Command, SIGNAL('clicked()'), self.createCommand)
        self.connect(self.pB_Clear, SIGNAL('clicked()'), self.clearAll)
        self.connect(self.pB_Quit, SIGNAL('clicked()'), self.close)
        self.connect(self.pB_sscan_Calc, SIGNAL('clicked()'), self.calc_sscan)
        self.connect(self.pB_cscan_Calc, SIGNAL('clicked()'), self.calc_cscan)
        self.connect(self.pB_ttscan_Calc, SIGNAL('clicked()'), self.calc_ttscan)
        self.connect(self.pB_qscan_Calc, SIGNAL('clicked()'), self.calc_qscan)

        self.connect(self.rB_qsscan, SIGNAL('clicked()'), self.set_qlabels)
        self.connect(self.rB_qcscan, SIGNAL('clicked()'), self.set_qlabels)
        self.connect(self.rB_qlscan, SIGNAL('clicked()'), self.set_qlabels)
        self.connect(self.rB_qtscan, SIGNAL('clicked()'), self.set_qlabels)
        self.connect(self.rB_qrscan, SIGNAL('clicked()'), self.set_qlabels)

        self.setWindowTitle(custom.CUSTOMNAME + ' - Command Generator')

        for lb in (self.lB_sscan_Device, self.lB_cscan_Device):
            for name, unit in custom.SCANDEVICES:
                lb.addItem("%s [%s]" % (name, unit))

        for name1, name2 in custom.TTSCANDEVICES:
            self.lB_ttscan_Device.addItem("%s, %s" % (name1, name2))

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

        # sscan, cscan, ttscan tabs
        self.lE_sscan_Start.setValidator(dval)
        self.lE_sscan_Step.setValidator(dval)
        self.lE_sscan_NStep.setValidator(ival)
        self.lE_sscan_PresetS.setValidator(dval)
        self.lE_sscan_movetime.setValidator(dval)
        self.lE_cscan_Center.setValidator(dval)
        self.lE_cscan_Step.setValidator(dval)
        self.lE_cscan_NStep.setValidator(ival)
        self.lE_cscan_PresetS.setValidator(dval)
        self.lE_cscan_movetime.setValidator(dval)
        self.lE_ttscan_Start.setValidator(dval)
        self.lE_ttscan_Step.setValidator(dval)
        self.lE_ttscan_NStep.setValidator(ival)
        self.lE_ttscan_PresetS.setValidator(dval)
        self.lE_ttscan_movetime.setValidator(dval)

        self.presets = DlgPresets('scaninput', [
            # qscan tab
            (self.rB_qsscan, 1), (self.rB_qcscan, 0),
            (self.rB_qlscan, 0), (self.rB_qtscan, 0),
            (self.rB_qrscan, 0), (self.presetInput, 1000),
            (self.hInput, '0.0'), (self.kInput, '0.0'),
            (self.lInput, '0.0'), (self.EInput, '0.0'),
            (self.deltahInput, '0.0'), (self.deltakInput, '0.0'),
            (self.deltalInput, '0.0'), (self.deltaEInput, '0.0'),
            (self.deltaqInput, '0.0'), (self.stepsInput, 10),
            # sscan tab
            (self.lE_sscan_Start, '0.0'), (self.lE_sscan_Step, '0.0'),
            (self.lE_sscan_NStep, '0'), (self.lE_sscan_PresetS, '0.0'),
            (self.lB_sscan_Device, 'om [degrees]'),
            (self.lE_sscan_movetime, '0'),
            # cscan tab
            (self.lE_cscan_Center, '0.0'), (self.lE_cscan_Step, '0.0'),
            (self.lE_cscan_NStep, '0'), (self.lE_cscan_PresetS, '0.0'),
            (self.lB_cscan_Device, 'om [degrees]'),
            (self.lE_cscan_movetime, '0'),
            # ttscan tab
            (self.lE_ttscan_Start, '0.0'), (self.lE_ttscan_Step, '0.0'),
            (self.lE_ttscan_NStep, '0'), (self.lE_ttscan_PresetS, '0.0'),
            (self.lB_ttscan_Device, 'om, phi'),
            (self.lE_ttscan_movetime, '0'),
            # the tab itself
            (self.tabWidget, 0),
        ])
        self.presets.load()
        self.set_qlabels()

    def set_qlabels(self, *args):
        if self.rB_qcscan.isChecked() or self.rB_qsscan.isChecked():
            self.label_dh.setText(u'<b>∆h</b>')
            self.label_dk.setText(u'<b>∆k</b>')
            self.label_dl.setText(u'<b>∆l</b>')
            self.deltahInput.setEnabled(True)
            self.deltakInput.setEnabled(True)
            self.deltalInput.setEnabled(True)
            self.deltaqInput.setEnabled(False)
        elif self.rB_qlscan.isChecked() or self.rB_qtscan.isChecked():
            self.label_dh.setText('')
            self.label_dk.setText('')
            self.label_dl.setText('')
            self.deltahInput.setEnabled(False)
            self.deltakInput.setEnabled(False)
            self.deltalInput.setEnabled(False)
            self.deltaqInput.setEnabled(True)
        elif self.rB_qrscan.isChecked():
            self.label_dh.setText('<b>u</b>')
            self.label_dk.setText('<b>v</b>')
            self.label_dl.setText('<b>w</b>')
            self.deltahInput.setEnabled(True)
            self.deltakInput.setEnabled(True)
            self.deltalInput.setEnabled(True)
            self.deltaqInput.setEnabled(True)

    def close(self, *args):
        """
        Close the window and save the settings.
        """
        self.presets.save()
        self.accept()
        return True

    def clearAll(self):
        # Clear sscan
        self.lE_sscan_Start.clear()
        self.lE_sscan_Step.clear()
        self.lE_sscan_NStep.clear()
        self.lE_sscan_PresetS.clear()
        self.lE_sscan_PresetH.clear()
        self.lE_sscan_End.clear()
        self.lE_sscan_movetime.clear()
        # Clear cscan
        self.lE_cscan_Center.clear()
        self.lE_cscan_Step.clear()
        self.lE_cscan_NStep.clear()
        self.lE_cscan_PresetS.clear()
        self.lE_cscan_PresetH.clear()
        self.lE_cscan_LEnd.clear()
        self.lE_cscan_UEnd.clear()
        self.lE_cscan_TSteps.clear()
        self.lE_cscan_movetime.clear()
        # Clear ttscan
        self.lE_ttscan_Start.clear()
        self.lE_ttscan_Step.clear()
        self.lE_ttscan_NStep.clear()
        self.lE_ttscan_PresetS.clear()
        self.lE_ttscan_PresetH.clear()
        self.lE_ttscan_End.clear()
        self.lE_ttscan_movetime.clear()
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

    def calc_sscan(self):
        stepsize = tofloat(self.lE_sscan_Step.text())
        numstep = toint(self.lE_sscan_NStep.text())
        startpos = tofloat(self.lE_sscan_Start.text())
        endpos = stepsize * numstep + startpos
        movetime = tofloat(self.lE_sscan_movetime.text())
        preset = tofloat(self.lE_sscan_PresetS.text())
        self.lE_sscan_End.setText("%.2f" % endpos)

        seconds = (movetime + preset) * numstep
        self.lE_sscan_PresetH.setText(fmt_time(seconds))
        return seconds

    def calc_cscan(self):
        stepsize = tofloat(self.lE_cscan_Step.text())
        numstep = toint(self.lE_cscan_NStep.text())
        center = tofloat(self.lE_cscan_Center.text())
        lowerend = - (stepsize * numstep) + center
        upperend = stepsize * numstep + center
        totalsteps = stepsize * numstep * 2
        movetime = tofloat(self.lE_cscan_movetime.text())
        preset = tofloat(self.lE_cscan_PresetS.text())
        self.lE_cscan_LEnd.setText("%.2f" % lowerend)
        self.lE_cscan_UEnd.setText("%.2f" % upperend)
        self.lE_cscan_TSteps.setText("%.2f" % totalsteps)

        seconds = (movetime + preset) * (numstep*2 + 1)
        self.lE_cscan_PresetH.setText(fmt_time(seconds))
        return seconds

    def calc_ttscan(self):
        stepsize = tofloat(self.lE_ttscan_Step.text())
        numstep = toint(self.lE_ttscan_NStep.text())
        startpos = tofloat(self.lE_ttscan_Start.text())
        endpos = stepsize * numstep + startpos
        movetime = tofloat(self.lE_ttscan_movetime.text())
        preset = tofloat(self.lE_ttscan_PresetS.text())
        self.lE_ttscan_End.setText("%.2f" % endpos)

        seconds = (movetime + preset) * numstep
        self.lE_ttscan_PresetH.setText(fmt_time(seconds))
        return seconds

    def calc_qscan(self):
        numstep = toint(self.stepsInput.text())
        if self.rB_qcscan.isChecked() or self.rB_qlscan.isChecked() or \
               self.rB_qtscan.isChecked():
            numstep = 2*numstep + 1
        preset = tofloat(self.presetInput.text())
        seconds = numstep * preset
        self.lE_qscan_PresetH.setText(fmt_time(seconds))
        return seconds

    def createCommand(self):
        tab = self.tabWidget.currentIndex()

        def timeest(secs):
            return '#- %d sec (%s)\n' % (secs, fmt_time(secs))

        # Qscan
        if tab == 3:
            paramctls = [
                ('Qh', self.hInput, tofloat),
                ('Qk', self.kInput, tofloat),
                ('Ql', self.lInput, tofloat),
                ('ny', self.EInput, tofloat),
                ('numsteps', self.stepsInput, toint),
            ]

            if self.rB_qcscan.isChecked() or self.rB_qsscan.isChecked():
                scan = self.rB_qcscan.isChecked() and 'qcscan' or 'qsscan'
                paramctls.extend([('dQh', self.deltahInput, tofloat),
                                  ('dQk', self.deltakInput, tofloat),
                                  ('dQl', self.deltalInput, tofloat),
                                  ('dny', self.deltaEInput, tofloat),])
            elif self.rB_qlscan.isChecked() or self.rB_qtscan.isChecked():
                scan = self.rB_qlscan.isChecked() and 'qlscan' or 'qtscan'
                paramctls.extend([('dq', self.deltaqInput, tofloat),
                                  ('dny', self.deltaEInput, tofloat),])
            elif self.rB_qrscan.isChecked():
                scan = 'qrscan'
                paramctls.extend([('u', self.deltahInput, tofloat),
                                  ('v', self.deltakInput, tofloat),
                                  ('w', self.deltalInput, tofloat),
                                  ('dq', self.deltaqInput, tofloat),
                                  ('dny', self.deltaEInput, tofloat),])

            params = []
            for (pn, ctl, fn) in paramctls:
                val = fn(ctl.text())
                if val: params.append("%s=%s" % (pn, val))

            cmd = timeest(self.calc_qscan())
            cmd += '%s(%s)\n' % (scan, ', '.join(params))

        # sscan
        elif tab == 0:
            devname = custom.SCANDEVICES[self.lB_sscan_Device.currentRow()][0]

            params = [devname]
            for (pn, ctl, fn) in (('start', self.lE_sscan_Start, tofloat),
                                  ('step', self.lE_sscan_Step, tofloat),
                                  ('numsteps', self.lE_sscan_NStep, toint),
                                  ('preset', self.lE_sscan_PresetS, tofloat)):
                val = fn(ctl.text())
                params.append("%s=%s" % (pn, val))

            cmd = timeest(self.calc_cscan())
            cmd += 'sscan(%s)\n' % ', '.join(params)

        # cscan
        elif tab == 1:
            devname = custom.SCANDEVICES[self.lB_cscan_Device.currentRow()][0]

            params = [devname]
            for (pn, ctl, fn) in (('center', self.lE_cscan_Center, tofloat),
                                  ('step', self.lE_cscan_Step, tofloat),
                                  ('numperside', self.lE_cscan_NStep, toint),
                                  ('preset', self.lE_cscan_PresetS, tofloat)):
                val = fn(ctl.text())
                params.append("%s=%s" % (pn, val))

            cmd = timeest(self.calc_cscan())
            cmd += 'cscan(%s)\n' % ', '.join(params)

        # ttscan
        elif tab == 2:
            params = list(custom.TTSCANDEVICES[
                    self.lB_ttscan_Device.currentRow()])
            for (pn, ctl, fn) in (('start', self.lE_ttscan_Start, tofloat),
                                  ('step', self.lE_ttscan_Step, tofloat),
                                  ('numsteps', self.lE_ttscan_NStep, toint),
                                  ('preset', self.lE_ttscan_PresetS, tofloat)):
                val = fn(ctl.text())
                params.append("%s=%s" % (pn, val))

            cmd = timeest(self.calc_ttscan())
            cmd += 'ttscan(%s)\n' % ', '.join(params)

        self.emit(SIGNAL("commandCreated"), cmd)
        print cmd


if __name__ == "__main__":
    runDlgStandalone(ScanInputDlg)
