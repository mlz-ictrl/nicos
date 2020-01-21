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
#   Alexander Steffens <a.steffens@fz-juelich.de>
#   Michael Wagener <m.wagener@fz-juelich.de>
#
# *****************************************************************************

"""Direct manual control of KWS-1 Hexapod via Tango controller device."""

from __future__ import absolute_import, division, print_function

import PyTango

from nicos.clients.gui.utils import DlgUtils, loadUi
from nicos.guisupport.qt import QMainWindow, QTimer, pyqtSlot
from nicos.utils import findResource

TANGO_DEV_BASE = 'tango://phys.kws1.frm2:10000/kws1/hexapod/h_'
AXES = ['tx', 'ty', 'tz', 'rz', 'ry', 'rx', 'omega']


class HexapodTool(DlgUtils, QMainWindow):
    toolName = 'HexapodTool'

    def __init__(self, parent, _client, **_kwds):
        QMainWindow.__init__(self, parent)
        DlgUtils.__init__(self, 'Hexapod')

        # set during actions that will call signal handlers
        self.recursive = False

        loadUi(self, findResource('nicos_mlz/kws1/gui/tools/hexapod.ui'))

        for but in (self.butStart, self.butSetWorkspace, self.butSetFrame,
                    self.butSaveVel):
            but.setEnabled(False)

        self.axes = {}
        self.axeslist = []

        try:
            self._controller = PyTango.DeviceProxy(
                TANGO_DEV_BASE + 'controller')
            # make sure the server is running and create remaining proxies
            try:
                self._controller.State()
            except AttributeError:
                raise Exception('server appears to be not running')
            for axis in AXES:
                self.axes[axis] = PyTango.DeviceProxy(TANGO_DEV_BASE + axis)
                self.axeslist.append(self.axes[axis])
        except Exception as err:
            self.showError('could not connect to tango server: %s' % err)
            self.deleteLater()
            return

        self.on_cbsWorkspace_activated(0)
        self.on_cbsFrame_activated(self.cbsFrame.currentText())

        tx_speed = self.query_attr(self.axes['tx'], 'speed')
        self.inpVelTrans.setValue(tx_speed)
        self.lblVelTrans.setText(self.inpVelTrans.text())
        self.inpVelRot.setValue(self.query_attr(self.axes['rx'], 'speed'))
        self.lblVelRot.setText(self.inpVelRot.text())
        self.inpVelOmega.setValue(self.query_attr(self.axes['omega'], 'speed'))
        self.lblVelOmega.setText(self.inpVelOmega.text())

        # ramp time = speed / acceleration
        self.inpRampUp.setValue(
            tx_speed / self.query_attr(self.axes['tx'], 'accel'))
        self.lblRampUp.setText(self.inpRampUp.text())
        self.inpRampDown.setValue(
            tx_speed / self.query_attr(self.axes['tx'], 'decel'))
        self.lblRampDown.setText(self.inpRampDown.text())

        self.updTimer = QTimer()
        self.updTimer.timeout.connect(self.updateTimer)
        self.updTimer.start(1000)

    def exec_cmd(self, dev, cmd, args=None):
        try:
            return dev.command_inout(cmd, args)
        except Exception as err:
            self.showError('could not execute %s on hexapod:\n%s' % (cmd, err))
            raise

    def query_attr(self, dev, attr):
        try:
            return getattr(dev, attr)
        except Exception as err:
            self.showError('could not query %s on hexapod:\n%s' % (attr, err))
            raise

    def set_attr(self, dev, attr, value):
        try:
            setattr(dev, attr, value)
        except Exception as err:
            self.showError('could not set %s on hexapod:\n%s' % (attr, err))
            raise

    @pyqtSlot()
    def on_butExit_clicked(self):
        self.close()
        self.deleteLater()

    def on_inpNewXX_valueChanged(self, v):
        self.butStart.setEnabled(True)

    @pyqtSlot()
    def on_butStart_clicked(self):
        self.exec_cmd(self._controller, 'StartSynchronousMovement', [
            self.inpNewTX.value(), self.inpNewTY.value(),
            self.inpNewTZ.value(), self.inpNewRZ.value(),
            self.inpNewRY.value(), self.inpNewRX.value(),
            self.inpNewOmega.value(), 0.0,  # detector arm dummy value
        ])
        self.butStart.setEnabled(False)

    @pyqtSlot()
    def on_butStop_clicked(self):
        try:
            self.exec_cmd(self._controller, 'Stop')
        except Exception as err:
            self.showInfo('exception raised after executing stop on hexapod:\n'
                          '%s' % err)

    def updateTimer(self):
        msg = '<font color=darkblue>' + self.exec_cmd(self._controller,
                                                      'Status')
        if 'not referenced' in self.exec_cmd(self.axes['omega'], 'Status'):
            msg += ' (omega not referenced)'
        msg += '</font>'
        self.lblStatus.setText(msg)

        pos = [self.query_attr(axis, 'value') for axis in self.axeslist]
        for value, widget in zip(pos, [
                self.lblCurTX, self.lblCurTY, self.lblCurTZ, self.lblCurRZ,
                self.lblCurRY, self.lblCurRX, self.lblCurOmega]):
            widget.setText('%8.3f' % value)

    @pyqtSlot(str)
    def on_cbsFrame_activated(self, text):
        frame = text.split()[0].upper()
        values = self.query_attr(self._controller, 'frame' + frame)
        for value, widget in zip(values, [
                self.inpFrameTX, self.inpFrameTY, self.inpFrameTZ,
                self.inpFrameRZ, self.inpFrameRY, self.inpFrameRX]):
            widget.setValue(value)
        self.butSetFrame.setEnabled(False)

    def on_inpFrameXX_valueChanged(self, _value):
        if self.cbsFrame.currentIndex() <= 3:
            self.butSetFrame.setEnabled(True)

    def on_inpWsXX_valueChanged(self, _value):
        if not self.recursive:
            self.butSetWorkspace.setEnabled(True)

    @pyqtSlot()
    def on_butSetWorkspace_clicked(self):
        self.recursive = True
        try:
            index = self.cbsWorkspace.currentIndex()
            group, index = ('juelich', index - 1) if index else ('hexamove', 0)
            workspaces = self.query_attr(self._controller,
                                         group + 'workspaceDefinitions')
            workspaces = [[i] + (ws if i != index else [
                self.inpWsTXmin.value(), self.inpWsTXmax.value(),
                self.inpWsTYmin.value(), self.inpWsTYmax.value(),
                self.inpWsTZmin.value(), self.inpWsTZmax.value(),
                self.inpWsRZmin.value(), self.inpWsRZmax.value(),
                self.inpWsRYmin.value(), self.inpWsRYmax.value(),
                self.inpWsRXmin.value(), self.inpWsRXmax.value(),
                self.inpWsTXref.value(), self.inpWsTYref.value(),
                self.inpWsTZref.value(), self.inpWsRZref.value(),
                self.inpWsRYref.value(), self.inpWsRXref.value(),
            ]) for i, ws in enumerate(workspaces)]
            self._controller.set_property(
                {'init{}workspaces'.format(group): workspaces})
        finally:
            self.recursive = False

    def on_togEnableWorkspace_toggled(self, checked):
        if self.recursive:
            return
        index = self.cbsWorkspace.currentIndex()
        group, index = ('juelich', index - 1) if index else ('hexamove', 0)
        self.exec_cmd(
            self._controller,
            ('Enable' if checked else 'Disable') + group + 'Workspace',
            index,
        )

    @pyqtSlot(int)
    def on_cbsWorkspace_activated(self, index):
        group, index = ('juelich', index - 1) if index else ('hexamove', 0)
        workspace = enabled = []
        for _ in range(5):
            workspace = self.query_attr(
                self._controller, group + 'WorkspaceDefinitions')[index]
            enabled = self.query_attr(
                self._controller, group + 'WorkspaceStatus')[index]
            # check reference frame values; if they are out of range then
            # do a few retries (the library sometimes returns dummy values)
            # TODO: check if this is still necessary with the new protocol
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
        self.set_attr(self._controller, 'manualControl', checked)
        self.grpFrames.setEnabled(not checked)
        self.grpNewPos.setEnabled(not checked)
        self.grpWorkspaces.setEnabled(not checked)

    @pyqtSlot()
    def on_butResetSystem_clicked(self):
        self.exec_cmd(self._controller, 'Reset')

    @pyqtSlot()
    def on_butCopyCurrent_clicked(self):
        for inwidget, labelwidget in zip([
                self.inpNewTX, self.inpNewTY, self.inpNewTZ,
                self.inpNewRZ, self.inpNewRY, self.inpNewRX,
                self.inpNewOmega], [
                    self.lblCurTX, self.lblCurTY, self.lblCurTZ,
                    self.lblCurRZ, self.lblCurRY, self.lblCurRX,
                    self.lblCurOmega]):
            inwidget.setValue(float(labelwidget.text().replace(',', '.')))

    @pyqtSlot()
    def on_actionReference_drive_triggered(self):
        self.exec_cmd(self.axes['omega'], 'Reference')

    @pyqtSlot()
    def on_actionSet_Zero_triggered(self):
        self.exec_cmd(self.axes['omega'], 'Adjust', 0)

    def on_inpVelXX_valueChanged(self, _v):
        self.butSaveVel.setEnabled(True)

    @pyqtSlot()
    def on_butSaveVel_clicked(self):
        self.set_attr(self.axes['tx'], 'speed', self.inpVelTrans.value())
        self.set_attr(self.axes['rx'], 'speed', self.inpVelRot.value())
        self.set_attr(self.axes['omega'], 'speed', self.inpVelOmega.value())
        # acceleration = speed / ramp time
        self.set_attr(self.axes['tx'], 'accel',
                      self.inpVelTrans.value() / self.inpRampUp.value())
        self.set_attr(self.axes['tx'], 'decel',
                      self.inpVelTrans.value() / self.inpRampDown.value())
        self.butSaveVel.setEnabled(False)

        self.lblVelTrans.setText(self.inpVelTrans.text())
        self.lblVelRot.setText(self.inpVelRot.text())
        self.lblVelOmega.setText(self.inpVelOmega.text())
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

    def on_inpNewOmega_valueChanged(self, v):
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

    def on_inpVelOmega_valueChanged(self, v):
        self.on_inpVelXX_valueChanged(v)

    def on_inpVelRot_valueChanged(self, v):
        self.on_inpVelXX_valueChanged(v)
