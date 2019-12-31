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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Panel to control special parameters and functions of a MLZ-PLC device."""

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QListWidgetItem, QMessageBox, Qt, \
    QTableWidgetItem, pyqtSlot
from nicos.utils import findResource


class PlcDeviceControlPanel(Panel):
    panelName = 'PLC device control'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_mlz/gui/plcpanel.ui'))
        self._curdev = None
        self._changed_pars = {}
        self._in_reread = False

        if client.isconnected:
            self.on_client_connected()
        client.connected.connect(self.on_client_connected)
        client.device.connect(self.on_client_device)

        self.controlBox.setEnabled(False)

    def on_client_connected(self):
        self._update_devices()

    def on_client_device(self):
        self._update_devices()

    def _update_devices(self):
        self.deviceBox.clear()
        candidates = self.client.getDeviceList(
            'nicos.devices.tango.PyTangoDevice',
            only_explicit=False,
        )
        self.deviceBox.addItems(
            [candidate for candidate in candidates
             if self.client.eval('session.getDevice(%r)._getProperty'
                                 '("plc_specification")' % candidate,
                                 default=None)])

    def on_deviceBox_currentIndexChanged(self, index):
        self.on_paramRereadBtn_clicked()

    @pyqtSlot()
    def on_paramRereadBtn_clicked(self):
        devname = self.deviceBox.currentText()
        if devname == self._curdev:
            return
        self._in_reread = True
        try:
            self._update_device(devname)
        finally:
            self._in_reread = False
            self._curdev = devname

    def _update_device(self, devname):
        try:
            parlist = self.client.eval('session.getDevice(%r)._dev.'
                                       'ListParams()' % devname)
            cmdlist = self.client.eval('session.getDevice(%r)._dev.'
                                       'ListCmds()' % devname)
        except Exception:
            QMessageBox.warning(self, 'Error', 'Could not retrieve the param/'
                                'command list from device.')
            return
        self.controlBox.setEnabled(True)

        self._par_values = {}
        self._changed_pars = {}
        self.paramTable.clear()
        self.paramTable.setColumnCount(2)
        self.paramTable.setRowCount(len(parlist))
        for (i, par) in enumerate(parlist):
            nameitem = QTableWidgetItem(par)
            nameitem.setFlags(nameitem.flags() & ~Qt.ItemIsEditable)
            self.paramTable.setItem(i, 0, nameitem)
            value = self.client.eval('session.getDevice(%r)._dev.'
                                     'GetParam(%r)' % (devname, par),
                                     default=None)
            valuestr = '<error>' if value is None else '%.6g' % value
            self._par_values[par] = valuestr
            self.paramTable.setItem(i, 1, QTableWidgetItem(valuestr))
        self.paramTable.resizeRowsToContents()
        self.paramTable.resizeColumnToContents(0)

        self.cmdList.clear()
        for cmd in cmdlist:
            QListWidgetItem(cmd, self.cmdList)

    def on_paramTable_itemChanged(self, item):
        if self._in_reread:
            return
        # someone edited the cell
        name = self.paramTable.item(item.row(), 0).text()
        try:
            value = float(item.text())
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Invalid value; should be a '
                                'floating point number.')
            self._in_reread = True
            item.setText(self._par_values[name])
            self._in_reread = False
            return
        self._par_values[name] = item.text()
        self._changed_pars[name] = value

    @pyqtSlot()
    def on_paramSetBtn_clicked(self):
        if not self._changed_pars:
            QMessageBox.warning(self, 'Nothing to do', 'No params have been '
                                'changed in the table.')
            return
        for name, value in self._changed_pars.items():
            try:
                self.client.eval('session.getDevice(%r)._dev.'
                                 'SetParam(([%r], [%r]))' %
                                 (self._curdev, value, name))
            except Exception:
                QMessageBox.warning(self, 'Error', 'Failed to set the %s '
                                    'parameter.' % name)
        QMessageBox.information(self, 'Info', 'All parameters have been set.')

    @pyqtSlot()
    def on_cmdExecBtn_clicked(self):
        cmd = self.cmdList.currentItem().text()
        arg = self.argEdit.text()
        if not arg:
            arg = '0'
        try:
            arg = float(arg)
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Invalid value; should be a '
                                'floating point number.')
            return
        try:
            self.client.eval('session.getDevice(%r)._dev.'
                             'SpecialCmd(([%r], [%r]))' %
                             (self._curdev, arg, cmd))
        except Exception:
            QMessageBox.warning(self, 'Error', 'Failed to execute the %s '
                                'command.' % cmd)
