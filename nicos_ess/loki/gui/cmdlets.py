#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

"""Commandlets for LoKI."""

from nicos.clients.gui.cmdlets import Cmdlet, register
from nicos.guisupport.qt import QDialog, QIcon, QMessageBox, QSize, \
    QTableWidgetItem, QToolButton, pyqtSlot
from nicos.utils import findResource, formatDuration

from nicos_ess.loki.gui.measdialogs import LOOPS, DetsetDialog, \
    DevicesDialog, MeasDef, RtConfigDialog, SampleDialog
from nicos_ess.loki.gui.measelement import Sample, Device


class MeasureTable(Cmdlet):

    name = 'Measurement'
    category = 'Measure'

    meas_def_class = MeasDef

    def __init__(self, parent, client):
        uipath = findResource('nicos_ess/loki/gui/ui_files/table.ui')
        Cmdlet.__init__(self, parent, client, uipath)
        self.measdef = self.meas_def_class(rtmode=False)
        self.rt_settings = RtConfigDialog.DEFAULT_SETTINGS.copy()
        self.rtConfBtn.setEnabled(False)
        self.updateTable()
        for loop in LOOPS:
            self.outerLoop.addItem(loop)
        self.outerLoop.setCurrentIndex(0)
        client.experiment.connect(self.on_client_experiment)
        self.expandBtn = QToolButton()
        self.expandBtn.setIcon(QIcon(':/down'))
        self.expandBtn.setAutoRaise(True)
        self.expandBtn.clicked.connect(self.on_expandBtn_clicked)
        self.table.setCornerWidget(self.expandBtn)

    @pyqtSlot()
    def on_expandBtn_clicked(self):
        self.table.setMinimumSize(QSize(0, self.table.height() + 100))

    @pyqtSlot()
    def on_selSamples_clicked(self):
        if not self.client.isconnected:
            QMessageBox.warning(self, 'Error', 'You must be connected to '
                                'a daemon to be able to select samples.')
            return
        dlg = SampleDialog(self, self.measdef, self.client)
        if dlg.exec_() != QDialog.Accepted:
            return
        self.measdef.samplefile = dlg.samplefile
        self.measdef.samples = dlg.toDefs()
        self.updateTable()

    @pyqtSlot()
    def on_selDetsets_clicked(self):
        if not self.client.isconnected:
            QMessageBox.warning(self, 'Error', 'You must be connected to '
                                'a daemon to be able to select settings.')
            return
        dlg = DetsetDialog(self, self.measdef, self.client)
        if dlg.exec_() != QDialog.Accepted:
            return
        self.measdef.detsets = dlg.toDefs()
        self.updateTable()

    @pyqtSlot()
    def on_selDevices_clicked(self):
        if not self.client.isconnected:
            QMessageBox.warning(self, 'Error', 'You must be connected to '
                                'a daemon to be able to select devices.')
            return
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
                if mloop:
                    self.updateTable()
                break
        self.innerLoop.setCurrentIndex(0)

    def on_client_experiment(self, data):
        # reset everything
        self.rtBox.setChecked(False)
        self._clearTable()

    def on_rtBox_toggled(self, state):
        self.rtConfBtn.setEnabled(state)
        self._clearTable()

    def _clearTable(self):
        self.measdef = self.meas_def_class(self.rtBox.isChecked(), self.measdef.loops)
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
            for j, element in enumerate(entry.values()):
                item = QTableWidgetItem(element.getDispValue())
                self.table.setItem(i, j, item)
                if element.eltype == 'time':
                    total_time += element.getValue()
        self.table.resizeRowsToContents()
        if self.rtBox.isChecked():
            total_time = self.rt_settings['totaltime'] * len(table)
        self.totalTime.setText(formatDuration(total_time))
        self.changed()

    def generate(self, mode):
        out = []
        table = self.measdef.getTable()
        for entry in table:
            items = []
            sample = None
            count_time = 0
            devices_args = []
            for (k, v) in entry.items():
                if isinstance(v, Sample):
                    sample = v.getValue()
                    count_time = v.extra[1]
                elif isinstance(v, Device):
                    devices_args.append(k)
                    devices_args.append(repr(v.getValue()))

            items.append(f"\n##### Measurement {len(out) + 1}")
            if sample:
                items.append(f'# SelectSample("{sample}")')
            if devices_args:
                args = ", ".join(devices_args)
                items.append(f"maw({args})")

            items.append(f"# loki_count(t={count_time})")
            out.append('\n'.join(items))
        return '\n'.join(out)


register(MeasureTable)
