#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Michael Wagener <m.wagener@fz-juelich.de>
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Direct manual control of KWS-1 Hexapod via Tango special device."""

from PyQt4.QtCore import QTimer, pyqtSlot
from PyQt4.QtGui import QMainWindow

import PyTango

from nicos.clients.gui.utils import loadUi, DlgUtils
from nicos.utils import findResource


TANGO_DEV_BASE = 'tango://phys.kws1.frm2:10000/kws1/hexapod'
AXES = ['tx', 'ty', 'tz', 'rz', 'ry', 'rx', 'dt']


class HexapodTool(QMainWindow, DlgUtils):
    toolName = 'HexapodTool'

    def __init__(self, parent, client, **kwds):
        QMainWindow.__init__(self, parent)
        DlgUtils.__init__(self, 'Hexapod')

        # set during actions that will call signal handlers
        self.recursive = False

        loadUi(self, findResource('custom/kws1/lib/gui/tools/hexapod.ui'))

        for but in (self.butStart, self.butSetWorkspace, self.butSetFrame,
                    self.butSaveVel):
            but.setEnabled(False)

        self.axes = {}
        self.axeslist = []

        try:
            self.special = PyTango.DeviceProxy(TANGO_DEV_BASE + 'special/1')
            # make sure the server is running and
            try:
                self.special.GlobalState()
            except AttributeError:
                raise Exception('server appears to be not running')
            for axis in AXES:
                self.axes[axis] = PyTango.DeviceProxy(TANGO_DEV_BASE + 'base/' + axis)
                self.axeslist.append(self.axes[axis])
        except Exception as err:
            self.showError('Could not connect to Tango server: %s' % err)
            self.deleteLater()
            return

        self.on_cbsWorkspace_activated(0)
        self.on_cbsFrame_activated(self.cbsFrame.currentText())

        self.inpVelTrans.setValue(self.query_attr(self.axes['tx'], 'speed'))
        self.lblVelTrans.setText(self.inpVelTrans.text())
        self.inpVelRot.setValue(self.query_attr(self.axes['rx'], 'speed'))
        self.lblVelRot.setText(self.inpVelRot.text())
        self.inpVelDT.setValue(self.query_attr(self.axes['dt'], 'speed'))
        self.lblVelDT.setText(self.inpVelDT.text())

        self.inpRampUp.setValue(self.query_attr(self.axes['tx'], 'accel'))
        self.lblRampUp.setText(self.inpRampUp.text())
        self.inpRampDown.setValue(self.query_attr(self.axes['tx'], 'decel'))
        self.lblRampDown.setText(self.inpRampDown.text())

        self.updTimer = QTimer()
        self.updTimer.timeout.connect(self.updateTimer)
        self.updTimer.start(1000)

    def exec_cmd(self, dev, cmd, *args):
        try:
            return getattr(dev, cmd)(*args)
        except Exception as err:
            # try once to switch device On
            try:
                dev.On()
                return getattr(dev, cmd)(*args)
            except Exception as err:
                self.showError('Could not execute %s on hexapod:\n%s' %
                               (cmd, err))
                raise

    def query_attr(self, dev, attr):
        try:
            return getattr(dev, attr)
        except Exception as err:
            # try once to switch device On
            try:
                dev.On()
                return getattr(dev, attr)
            except Exception as err:
                self.showError('Could not query %s on hexapod:\n%s' %
                               (attr, err))
                raise

    def set_attr(self, dev, attr, value):
        try:
            setattr(dev, attr, value)
        except Exception as err:
            # try once to switch device On
            try:
                dev.On()
                setattr(dev, attr, value)
            except Exception as err:
                self.showError('Could not set %s on hexapod:\n%s' %
                               (attr, err))
                raise

    @pyqtSlot()
    def on_butExit_clicked(self):
        self.close()
        self.deleteLater()

    def on_inpNewXX_valueChanged(self, v):
        self.butStart.setEnabled(True)

    @pyqtSlot()
    def on_butStart_clicked(self):
        for client, widget in zip(self.axeslist, [
                self.inpNewTX, self.inpNewTY, self.inpNewTZ,
                self.inpNewRZ, self.inpNewRY, self.inpNewRX, self.inpNewDT]):
            self.set_attr(client, 'value', widget.value())
        self.butStart.setEnabled(False)

    @pyqtSlot()
    def on_butStop_clicked(self):
        for axis in self.axeslist:
            try:
                self.exec_cmd(axis, 'Stop')
            except Exception:
                pass

    def updateTimer(self):
        msg = self.exec_cmd(self.axes['tx'], 'Status')
        # [ 0] = Hexamove::CheckCommunicationToMaster (0=ok)
        # [ 1] = Hexamove::GetEnableStatus (1=enabled)
        # [ 2] = Hexamove::GetEStopStatus (0=no EStop)
        # [ 3] = Drehtisch::GetIsDrehtishActive (1=active)
        # [ 4] = Drehtisch::GetIsDrehtischInstalled (NEW)
        # [ 5] = Drehtisch::GetIsDrehtischReferenzRunOk (NEW)
        flags = self.exec_cmd(self.special, 'GlobalState')

        msg += ('<br><font color=darkblue>Master: Comm=%s, Enable=%s, '
                'EStop=%s<br>DT: active=%s, installed=%s' % (
                    'ok' if flags[0] == 0 else 'FAIL',
                    'ena' if flags[1] == 1 else 'DIS',
                    'no' if flags[2] == 0 else 'ESTOP',
                    'ok' if flags[3] == 1 else 'DIS',
                    'yes' if flags[4] == 1 else 'NO'))
        if flags[5] != 328193:  # ER_INCO_VAR_NOT_FOUND
            msg += ', RefRun=%s' % ('ok' if flags[5] == 1 else 'NO')
        msg += '</font>'

        self.recursive = True
        try:
            self.actionInstall.setChecked(flags[4])
            self.actionEnable.setChecked(flags[3])
        finally:
            self.recursive = False

        self.lblStatus.setText(msg)

        pos = [self.query_attr(axis, 'value') for axis in self.axeslist]
        for value, widget in zip(pos, [
                self.lblCurTX, self.lblCurTY, self.lblCurTZ,
                self.lblCurRZ, self.lblCurRY, self.lblCurRX, self.lblCurDT]):
            widget.setText('%8.3f' % value)

    @pyqtSlot(str)
    def on_cbsFrame_activated(self, text):
        frame = text.split()[0]
        values = self.query_attr(self.special, 'frame' + frame)
        for value, widget in zip(values, [
                self.inpFrameTX, self.inpFrameTY, self.inpFrameTZ,
                self.inpFrameRZ, self.inpFrameRY, self.inpFrameRX]):
            widget.setValue(value)
        self.butSetFrame.setEnabled(False)

    def on_inpFrameXX_valueChanged(self, value):
        if self.cbsFrame.currentIndex() <= 3:
            self.butSetFrame.setEnabled(True)

    def on_inpWsXX_valueChanged(self, value):
        if not self.recursive:
            self.butSetWorkspace.setEnabled(True)

    @pyqtSlot()
    def on_butSetWorkspace_clicked(self):
        self.recursive = True
        try:
            workspaces = self.query_attr(self.special, 'workspaces')
            index = self.cbsWorkspace.currentIndex()
            workspaces[index] = [
                self.inpWsTXmin.value(), self.inpWsTXmax.value(),
                self.inpWsTYmin.value(), self.inpWsTYmax.value(),
                self.inpWsTZmin.value(), self.inpWsTZmax.value(),
                self.inpWsRZmin.value(), self.inpWsRZmax.value(),
                self.inpWsRYmin.value(), self.inpWsRYmax.value(),
                self.inpWsRXmin.value(), self.inpWsRXmax.value(),
                self.inpWsTXref.value(), self.inpWsTYref.value(),
                self.inpWsTZref.value(), self.inpWsRZref.value(),
                self.inpWsRYref.value(), self.inpWsRXref.value(),
            ]
            self.set_attr(self.special, 'workspaces', workspaces)
        finally:
            self.recursive = False

    def on_togEnableWorkspace_toggled(self, checked):
        if self.recursive:
            return
        index = self.cbsWorkspace.currentIndex()
        wsenabled = self.query_attr(self.special, 'workspacesEnabled')
        wsenabled[index] = int(checked)
        self.set_attr(self.special, 'workspacesEnabled', wsenabled)

    @pyqtSlot(int)
    def on_cbsWorkspace_activated(self, index):
        for _ in range(5):
            workspace = self.query_attr(self.special, 'workspaces')[index]
            enabled = self.query_attr(self.special, 'workspacesEnabled')[index]
            # check reference frame values; if they are out of range then
            # do a few retries (the library sometimes returns dummy values)
            reftx, refty, reftz, refrz, refry, refrx = workspace[-6:]
            if (-50 <= reftx <= +50) and (-50 <= refty <= +50) and \
               (-50 <= reftz <= 510) and (-5 <= refrx <= +5) and \
               (-5 <= refry <= +5) and (-180 <= refrz <= +180):
                break
        self.recursive = True
        try:
            for value, widget in zip(workspace, [
                    self.inpWsTXmin, self.inpWsTXmax,
                    self.inpWsTYmin, self.inpWsTYmax,
                    self.inpWsTZmin, self.inpWsTZmax,
                    self.inpWsRZmin, self.inpWsRZmax,
                    self.inpWsRYmin, self.inpWsRYmax,
                    self.inpWsRXmin, self.inpWsRXmax,
                    self.inpWsTXref, self.inpWsTYref,
                    self.inpWsTZref, self.inpWsRZref,
                    self.inpWsRYref, self.inpWsRXref,
            ]):
                widget.setValue(value)
            self.togEnableWorkspace.setChecked(enabled)
        finally:
            self.recursive = False
        self.butSetWorkspace.setEnabled(False)

    def on_togBirne_toggled(self, checked):
        if checked:
            self.set_attr(self.special, 'manualControl', True)
            self.grpFrames.setEnabled(False)
            self.grpNewPos.setEnabled(False)
            self.grpWorkspaces.setEnabled(False)
        else:
            self.set_attr(self.special, 'manualControl', False)
            self.grpFrames.setEnabled(True)
            self.grpNewPos.setEnabled(True)
            self.grpWorkspaces.setEnabled(True)

    @pyqtSlot()
    def on_butReEnableSystem_clicked(self):
        self.exec_cmd(self.special, 'EnableSystem')

    @pyqtSlot()
    def on_butCopyCurrent_clicked(self):
        for inwidget, labelwidget in zip([
                self.inpNewTX, self.inpNewTY, self.inpNewTZ,
                self.inpNewRZ, self.inpNewRY, self.inpNewRX,
                self.inpNewDT], [
                    self.lblCurTX, self.lblCurTY, self.lblCurTZ,
                    self.lblCurRZ, self.lblCurRY, self.lblCurRX,
                    self.lblCurDT]):
            inwidget.setValue(float(labelwidget.text().replace(',', '.')))

    @pyqtSlot()
    def on_actionReference_drive_triggered(self):
        self.exec_cmd(self.axes['dt'], 'Reference')

    def on_actionInstall_toggled(self, flag):
        if self.recursive:
            return
        # =0: Drehtisch Installed = false
        # =1: Drehtisch Installed = true
        # =2: Drehtisch Active = false
        # =3: Drehtisch Active = true
        self.exec_cmd(self.special, 'EnableTable', 1 if flag else 0)

    def on_actionEnable_toggled(self, flag):
        if self.recursive:
            return
        self.exec_cmd(self.special, 'EnableTable', 3 if flag else 2)

    @pyqtSlot()
    def on_actionSet_Zero_triggered(self):
        self.exec_cmd(self.axes['dt'], 'Reset')
        self.exec_cmd(self.axes['dt'], 'Adjust', 0)

    def on_inpVelXX_valueChanged(self, v):
        self.butSaveVel.setEnabled(True)

    @pyqtSlot()
    def on_butSaveVel_clicked(self):
        self.set_attr(self.axes['tx'], 'speed', self.inpVelTrans.value())
        self.set_attr(self.axes['rx'], 'speed', self.inpVelRot.value())
        self.set_attr(self.axes['dt'], 'speed', self.inpVelDT.value())
        self.set_attr(self.axes['tx'], 'accel', self.inpRampUp.value())
        self.set_attr(self.axes['tx'], 'decel', self.inpRampDown.value())
        self.butSaveVel.setEnabled(False)

        self.lblVelTrans.setText(self.inpVelTrans.text())
        self.lblVelRot.setText(self.inpVelRot.text())
        self.lblVelDT.setText(self.inpVelDT.text())
        self.lblRampUp.setText(self.inpRampUp.text())
        self.lblRampDown.setText(self.inpRampDown.text())

    def on_inpFrameTX_valueChanged(self, v):
        self.on_inpFrameXX_valueChanged(v)

    def on_inpFrameTY_valueChanged(self, v):
        self.on_inpFrameXX_valueChanged(v)

    def on_inpFrameTZ_valueChanged(self, v):
        self.on_inpFrameXX_valueChanged(v)

    def on_inpFrameRX_valueChanged(self, v):
        self.on_inpFrameXX_valueChanged(v)

    def on_inpFrameRY_valueChanged(self, v):
        self.on_inpFrameXX_valueChanged(v)

    def on_inpFrameRZ_valueChanged(self, v):
        self.on_inpFrameXX_valueChanged(v)

    def on_inpWsTXmax_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsTXmin_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsTXref_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsTYmax_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsTYmin_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsTYref_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsTZmax_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsTZmin_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsTZref_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsRXmax_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsRXmin_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsRXref_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsRYmax_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsRYmin_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsRYref_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsRZmax_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsRZmin_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpWsRZref_valueChanged(self, v):
        self.on_inpWsXX_valueChanged(v)

    def on_inpNewDT_valueChanged(self, v):
        self.on_inpNewXX_valueChanged(v)

    def on_inpNewRZ_valueChanged(self, v):
        self.on_inpNewXX_valueChanged(v)

    def on_inpNewRY_valueChanged(self, v):
        self.on_inpNewXX_valueChanged(v)

    def on_inpNewRX_valueChanged(self, v):
        self.on_inpNewXX_valueChanged(v)

    def on_inpNewTZ_valueChanged(self, v):
        self.on_inpNewXX_valueChanged(v)

    def on_inpNewTY_valueChanged(self, v):
        self.on_inpNewXX_valueChanged(v)

    def on_inpNewTX_valueChanged(self, v):
        self.on_inpNewXX_valueChanged(v)

    def on_inpRampDown_valueChanged(self, v):
        self.on_inpVelXX_valueChanged(v)

    def on_inpRampUp_valueChanged(self, v):
        self.on_inpVelXX_valueChanged(v)

    def on_inpVelTrans_valueChanged(self, v):
        self.on_inpVelXX_valueChanged(v)

    def on_inpVelDT_valueChanged(self, v):
        self.on_inpVelXX_valueChanged(v)

    def on_inpVelRot_valueChanged(self, v):
        self.on_inpVelXX_valueChanged(v)
