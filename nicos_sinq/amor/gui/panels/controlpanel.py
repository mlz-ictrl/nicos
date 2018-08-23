#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2018 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from logging import WARNING

from nicos.clients.gui.dialogs.error import ErrorDialog
from nicos.clients.gui.panels.generic import GenericPanel
from nicos.clients.gui.utils import ScriptExecQuestion
from nicos.guisupport.qt import QMessageBox, pyqtSlot, QRegExp, \
    QRegExpValidator
from nicos.guisupport.typedvalue import MissingWidget
from nicos.guisupport.widget import NicosWidget
from nicos.pycompat import iteritems


class AmorControlPanel(GenericPanel):

    def __init__(self, parent, client, options):
        GenericPanel.__init__(self, parent, client, options)
        for ch in self.findChildren(NicosWidget):
            ch.setClient(client)

        # daemon request ID of last command executed from this panel
        # (used to display messages from this command)
        self._current_status = 'idle'
        self._exec_reqid = None
        self._error_window = None

        self.motor_widgets = {
            'som': self.somEdit,
            's2t': self.s2tEdit,
            'soz': self.sozEdit,
            'stz': self.stzEdit
        }

        self.slit_widgets = {
            'slit1_opening': self.slit1Edit,
            'slit2_opening': self.slit2Edit,
            'slit3_opening': self.slit3Edit,
            'slit4_opening': self.slit4Edit,
            'd5v': self.slit5Edit,
        }

        self.magnet_widgets = {
            'hsy': self.hsyEdit
        }

        # Initialise the widgets
        self._reinit()

        # Set the validator for monitor preset edit
        # Regular expression for scientific notation: [\d.]+(?:e\d+)?
        self.monitorPresetBox.setValidator(
            QRegExpValidator(QRegExp(r"[\d.]+(?:e\d+)?"), self))

        self.setMonitorPreset(True)
        self.setSampleMove(True)

        self.opMonitor.toggled.connect(self.setMonitorPreset)
        self.opTime.toggled.connect(self.setTimePreset)
        self.opSampleMove.toggled.connect(self.setSampleMove)
        self.opSampleSetPosition.toggled.connect(self.setSampleSetPosition)
        client.message.connect(self.on_client_message)
        client.setup.connect(self.on_client_setup)

    def updateStatus(self, status, exception=False):
        self._current_status = status

    def _reinit(self):
        widgets_dict = {}
        widgets_dict.update(self.motor_widgets)
        widgets_dict.update(self.slit_widgets)
        widgets_dict.update(self.magnet_widgets)

        for n, w in iteritems(widgets_dict):
            currval = self.client.getDeviceParam(n, 'value')
            w._reinit(currval)

    def on_client_setup(self):
        self._reinit()

    def on_client_message(self, message):
        # show warnings and errors emitted by the current command in a window
        if message[5] != self._exec_reqid or message[2] < WARNING:
            return
        msg = '%s: %s' % (message[0], message[3].strip())
        if self._error_window is None:
            def reset_errorwindow():
                self._error_window = None
            self._error_window = ErrorDialog(self)
            self._error_window.accepted.connect(reset_errorwindow)
            self._error_window.addMessage(msg)
            self._error_window.show()
        else:
            self._error_window.addMessage(msg)
            self._error_window.activateWindow()
        self._reinit()

    def setMonitorPreset(self, checked):
        self.timePresetWidget.setVisible(not checked)
        self.monitorPresetWidget.setVisible(checked)

    def setTimePreset(self, checked):
        self.monitorPresetWidget.setVisible(not checked)
        self.timePresetWidget.setVisible(checked)

    def setSampleMove(self, checked):
        self.sampleSetPositionButtonWidget.setVisible(not checked)
        self.motor_widgets['s2t'].setEnabled(checked)
        self.sampleMoveButtonWidget.setVisible(checked)
        self._reinit()

    def setSampleSetPosition(self, checked):
        self.motor_widgets['s2t'].setEnabled(not checked)
        self.sampleMoveButtonWidget.setVisible(not checked)
        self.sampleSetPositionButtonWidget.setVisible(checked)
        self._reinit()

    def exec_command(self, command, ask_queue=True, immediate=False):
        if ask_queue and not immediate and self._current_status != 'idle':
            qwindow = ScriptExecQuestion()
            result = qwindow.exec_()
            if result == QMessageBox.Cancel:
                return
            elif result == QMessageBox.Apply:
                immediate = True
        if immediate:
            self.client.tell('exec', command)
            self._exec_reqid = None  # no request assigned to this command
        else:
            self._exec_reqid = self.client.run(command)

    @pyqtSlot()
    def on_countStartButton_clicked(self):
        if self.opTime.isChecked():
            value = float(self.timePresetBox.text())
            preset = 't'
        else:
            try:
                value = float(self.monitorPresetBox.text())
                preset = 'm'
            except ValueError:
                self.log.exception('invalid value for monitor preset')
                QMessageBox.warning(self, 'Error', 'Invalid monitor preset')
                return
        args = '%s=%r' % (preset, int(value))
        code = 'count(%s)' % args
        self.exec_command(code)

    @pyqtSlot()
    def on_sampleMoveButton_clicked(self):
        self._devsMoveButton(self.motor_widgets, 'move')

    @pyqtSlot()
    def on_sampleMoveAndWaitButton_clicked(self):
        self._devsMoveButton(self.motor_widgets, 'maw')

    @pyqtSlot()
    def on_sampleSetPositionButton_clicked(self):
        self._devsMoveButton(self.motor_widgets, 'adjust', True)

    @pyqtSlot()
    def on_slitMoveButton_clicked(self):
        self._devsMoveButton(self.slit_widgets, 'move')

    @pyqtSlot()
    def on_slitMoveAndWaitButton_clicked(self):
        self._devsMoveButton(self.slit_widgets, 'maw')

    @pyqtSlot()
    def on_hsyToggleButton_clicked(self):
        switchedOn = self.client.eval('hsy_switch.isSwitchedOn', None)
        if switchedOn is None:
            self.showError('Cannot check the status of magnets!')
        newstate = 'off' if switchedOn else 'on'
        code = 'hsy_switch.move(%r)' % newstate
        self.exec_command(code)

    @pyqtSlot()
    def on_hsyMoveButton_clicked(self):
        self._devsMoveButton(self.magnet_widgets, 'move')

    def _devsMoveButton(self, dic, cmd='move', issue_separate=False):
        dev_to_widget = {
            n: w for n, w in iteritems(dic) if not isinstance(w._inner,
                                                              MissingWidget)}
        targets = []
        try:
            targets = [edit.getValue() for edit in dev_to_widget.values()]
        except ValueError:
            self.log.exception('invalid value for typed value')
            # shouldn't happen, but if it does, at least gives indication that
            # something went wrong
            QMessageBox.warning(self, 'Error', 'Some entered value is invalid')
            return

        # Check which motors to move
        expr = ', '.join([
            n + '.isAtTarget(%r)' % v for n, v in zip(dev_to_widget, targets)])
        on_targ = self.client.eval(expr, None)
        if on_targ is None:
            self.showError('Cannot check the status! Cannot move!')
            return

        if not isinstance(on_targ, tuple):
            on_targ = [on_targ]

        move = {
            n: v for n, v, t in zip(dev_to_widget, targets, on_targ) if not t}

        if not move:
            return

        if issue_separate:
            code = '\n'.join(
                ('%s(%s, %r)' % (cmd, n, v) for n, v in iteritems(move)))
        else:
            code = '%s(%s)' % (cmd, ', '.join(
                ('%s, %r' % (n, v) for n, v in iteritems(move))))
        self.exec_command(code)
