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

"""Commandlets for KWS(-1)."""

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QDialog, QTableWidgetItem

from nicos.clients.gui.cmdlets import Cmdlet, register
from nicos.utils import findResource, formatDuration
from nicos.pycompat import srepr
from nicos.kws1.gui.measdialogs import MeasDef, SampleDialog, DetsetDialog, \
    DevicesDialog, RtConfigDialog, LOOPS

WIDGET_TYPE = 33


class MeasureTable(Cmdlet):

    name = 'Measurement'
    category = 'Measure'

    def __init__(self, parent, client):
        uipath = findResource('custom/kws1/lib/gui/table.ui')
        Cmdlet.__init__(self, parent, client, uipath)
        self.measdef = MeasDef(rtmode=False)
        self.rt_settings = RtConfigDialog.DEFAULT_SETTINGS.copy()
        self.rtConfBtn.setEnabled(False)
        self.updateTable()
        for loop in LOOPS:
            self.outerLoop.addItem(loop)
        self.outerLoop.setCurrentIndex(0)

    @pyqtSlot()
    def on_selSamples_clicked(self):
        dlg = SampleDialog(self, self.measdef, self.client)
        if dlg.exec_() != QDialog.Accepted:
            return
        self.measdef.samples = dlg.toDefs()
        self.updateTable()

    @pyqtSlot()
    def on_selDetsets_clicked(self):
        dlg = DetsetDialog(self, self.measdef, self.client)
        if dlg.exec_() != QDialog.Accepted:
            return
        self.measdef.detsets = dlg.toDefs()
        self.updateTable()

    @pyqtSlot()
    def on_selDevices_clicked(self):
        dlg = DevicesDialog(self, self.measdef, self.client)
        if dlg.exec_() != QDialog.Accepted:
            return
        self.measdef.devices = dlg.toDefs()
        self.updateTable()

    @pyqtSlot(str)
    def on_outerLoop_currentIndexChanged(self, oloop):
        self.middleLoop.clear()
        for loop in LOOPS:
            if loop != oloop:
                self.middleLoop.addItem(loop)
        self.middleLoop.setCurrentIndex(0)

    @pyqtSlot(str)
    def on_middleLoop_currentIndexChanged(self, mloop):
        oloop = self.outerLoop.currentText()
        self.innerLoop.clear()
        for loop in LOOPS:
            if loop != mloop and loop != oloop:
                self.innerLoop.addItem(loop)
                self.measdef.loops = [oloop, mloop, loop]
                self.updateTable()
                break
        self.innerLoop.setCurrentIndex(0)

    def on_rtBox_toggled(self, state):
        self.rtConfBtn.setEnabled(state)
        # clears current table!
        self.measdef = MeasDef(state)
        self.updateTable()

    @pyqtSlot()
    def on_rtConfBtn_clicked(self):
        dlg = RtConfigDialog(self)
        dlg.setSettings(self.rt_settings)
        if not dlg.exec_():
            return
        self.rt_settings = dlg.getSettings()

    def getValues(self):
        return {}

    def setValues(self, values):
        pass

    def updateTable(self):
        self.table.setRowCount(0)
        table = self.measdef.getTable()
        if not table:
            return
        first = table[0]
        self.table.setRowCount(len(table))
        self.table.setColumnCount(len(first))
        self.table.setHorizontalHeaderLabels(first.keys())
        total_time = 0
        for i, entry in enumerate(table):
            for j, value in enumerate(entry.values()):
                item = QTableWidgetItem(str(value.text))
                item.setData(WIDGET_TYPE, value.wclass)
                self.table.setItem(i, j, item)
                if value.ename == 'time':
                    total_time += value.key
        self.table.resizeRowsToContents()
        self.totalTime.setText(formatDuration(total_time))
        self.changed()

    def generate(self, mode):
        out = []
        if self.rtBox.isChecked():
            out.append('SetupRealtime(%d, %d, %f, %s)' % (
                self.rt_settings['channels'],
                self.rt_settings['interval'] *
                {0: 1, 1: 3, 2: 6}[self.rt_settings['intervalunit']],
                self.rt_settings['progq'],
                srepr(self.rt_settings['trigger']),
            ))
        else:
            out.append('SetupNormal()')
        table = self.measdef.getTable()
        # detect if we use a non-default value for these, and generate the
        # keywords only for these cases
        has_lenses = False
        has_chopper = False
        has_polarizer = False
        for entry in table:
            for (k, v) in entry.items():
                if k == 'chopper' and v.key != 'off':
                    has_chopper = True
                elif k == 'polarizer' and v.key != 'out':
                    has_polarizer = True
                elif k == 'lenses' and v.key != 'out-out-out':
                    has_lenses = True
        for entry in table:
            items = []
            for (k, v) in entry.items():
                if k == 'chopper' and not has_chopper:
                    continue
                if k == 'polarizer' and not has_polarizer:
                    continue
                if k == 'lenses' and not has_lenses:
                    continue
                items.append('%s=%s' % (k, srepr(v.key)))
            out.append('kwscount(' + ', '.join(items) + ')')
        return '\n'.join(out)


register(MeasureTable)
