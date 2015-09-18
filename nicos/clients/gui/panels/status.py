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

"""NICOS GUI script status panel component."""

import time

from PyQt4.QtGui import QToolBar, QMenu, QListWidgetItem, QIcon, \
    QPixmap, QColor
from PyQt4.QtCore import Qt, QTimer, SIGNAL
from PyQt4.QtCore import pyqtSignature as qtsig

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.utils import setBackgroundColor
from nicos.protocols.daemon import BREAK_NOW, BREAK_AFTER_STEP, \
    BREAK_AFTER_LINE


class ScriptQueue(object):
    def __init__(self, frame, view):
        self._no2item = {}   # mapping from request number to list widget item
        self._frame = frame
        self._view = view
        self._timer = QTimer(singleShot=True, timeout=self._timeout)

    def _format_item(self, request):
        script = request['script']
        if len(script) > 100:
            return script[:100] + '...'
        return script

    def _timeout(self):
        self._frame.show()

    def append(self, request):
        item = QListWidgetItem(self._format_item(request))
        item.setData(Qt.UserRole, request['reqno'])
        self._no2item[request['reqno']] = item
        self._view.addItem(item)
        # delay showing the frame for 20 msecs, so that it doesn't flicker in
        # and out if the script is immediately taken out of the queue again
        self._timer.start(20)

    def remove(self, reqno):
        item = self._no2item.pop(reqno, None)
        if item is None:
            return
        item = self._view.takeItem(self._view.row(item))
        if not self._no2item:
            self._timer.stop()
            self._frame.hide()
        return item

    def clear(self):
        self._frame.hide()
        self._view.clear()
        self._no2item.clear()

    def __nonzero__(self):
        return bool(self._no2item)

    __bool__ = __nonzero__


class ScriptStatusPanel(Panel):
    panelName = 'Script status'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'status.ui', 'panels')

        self.menus = None
        self.bar = None
        self.queueFrame.hide()
        self.statusLabel.hide()
        self.pause_color = QColor('#ffdddd')
        self.idle_color = parent.user_color

        self.script_queue = ScriptQueue(self.queueFrame, self.queueView)
        self.current_line = -1
        self.current_request = {}
        self.curlineicon = QIcon(':/currentline')
        empty = QPixmap(16, 16)
        empty.fill(Qt.transparent)
        self.otherlineicon = QIcon(empty)

        self.connect(client, SIGNAL('request'), self.on_client_request)
        self.connect(client, SIGNAL('processing'), self.on_client_processing)
        self.connect(client, SIGNAL('blocked'), self.on_client_blocked)
        self.connect(client, SIGNAL('status'), self.on_client_status)
        self.connect(client, SIGNAL('initstatus'), self.on_client_initstatus)
        self.connect(client, SIGNAL('disconnected'), self.on_client_disconnected)

        bar = QToolBar('Script control')
        bar.setObjectName(bar.windowTitle())
        # unfortunately it is not wise to put a menu in its own dropdown menu,
        # so we have to duplicate the actionBreak and actionStop...
        dropdown1 = QMenu('', self)
        dropdown1.addAction(self.actionBreak)
        dropdown1.addAction(self.actionBreakCount)
        self.actionBreak2.setMenu(dropdown1)
        dropdown2 = QMenu('', self)
        dropdown2.addAction(self.actionStop)
        dropdown2.addAction(self.actionFinish)
        self.actionStop2.setMenu(dropdown2)
        bar.addAction(self.actionBreak2)
        bar.addAction(self.actionContinue)
        bar.addAction(self.actionStop2)
        bar.addAction(self.actionEmergencyStop)
        self.mainwindow.addToolBar(bar)

        menu = QMenu('&Script control', self)
        menu.addAction(self.actionBreak)
        menu.addAction(self.actionBreakCount)
        menu.addAction(self.actionContinue)
        menu.addSeparator()
        menu.addAction(self.actionStop)
        menu.addAction(self.actionFinish)
        menu.addSeparator()
        menu.addAction(self.actionEmergencyStop)
        self.mainwindow.menuBar().insertMenu(
            self.mainwindow.menuWindows.menuAction(), menu)

    def setCustomStyle(self, font, back):
        self.idle_color = back
        for widget in (self.traceView, self.queueView):
            widget.setFont(font)
            setBackgroundColor(widget, back)

    def getToolbars(self):
        return []

    def getMenus(self):
        return []

    def updateStatus(self, status, exception=False):
        isconnected = status != 'disconnected'
        self.actionBreak.setEnabled(isconnected and status != 'idle')
        self.actionBreak2.setEnabled(isconnected and status != 'idle')
        self.actionBreak2.setVisible(status != 'paused')
        self.actionBreakCount.setEnabled(isconnected and status != 'idle')
        self.actionContinue.setVisible(status == 'paused')
        self.actionStop.setEnabled(isconnected and status != 'idle')
        self.actionStop2.setEnabled(isconnected and status != 'idle')
        self.actionFinish.setEnabled(isconnected and status != 'idle')
        self.actionEmergencyStop.setEnabled(isconnected)
        if status == 'paused':
            self.statusLabel.setText('Script is paused.')
            self.statusLabel.show()
            setBackgroundColor(self.traceView, self.pause_color)
        else:
            self.statusLabel.hide()
            setBackgroundColor(self.traceView, self.idle_color)
        self.traceView.update()

    def setScript(self, script):
        self.traceView.clear()
        for line in script.splitlines():
            item = QListWidgetItem(self.otherlineicon, line, self.traceView)
            self.traceView.addItem(item)
        self.current_line = -1

    def setCurrentLine(self, line):
        if self.current_line != -1:
            item = self.traceView.item(self.current_line - 1)
            if item:
                item.setIcon(self.otherlineicon)
            self.current_line = -1
        if 0 < line <= self.traceView.count():
            item = self.traceView.item(line - 1)
            item.setIcon(self.curlineicon)
            self.traceView.scrollToItem(item)
            self.current_line = line

    def on_client_request(self, request):
        if 'script' not in request:
            return
        self.script_queue.append(request)

    def on_client_processing(self, request):
        if 'script' not in request:
            return
        new_current_line = -1
        if self.current_request['reqno'] == request['reqno']:
            # on update, set the current line to the same as before
            # (this may be WRONG, but should not in most cases, and it's
            # better than no line indicator at all)
            new_current_line = self.current_line
        self.script_queue.remove(request['reqno'])
        self.setScript(request['script'])
        self.current_request = request
        self.setCurrentLine(new_current_line)

    def on_client_blocked(self, requests):
        for reqno in requests:
            self.script_queue.remove(reqno)

    def on_client_initstatus(self, state):
        self.setScript(state['script'])
        self.current_request['script'] = state['script']
        self.current_request['reqno'] = None
        self.on_client_status(state['status'])
        for req in state['requests']:
            self.on_client_request(req)

    def on_client_status(self, data):
        _status, line = data
        if line != self.current_line:
            self.setCurrentLine(line)

    def on_client_disconnected(self):
        self.script_queue.clear()

    @qtsig('')
    def on_actionBreak_triggered(self):
        self.mainwindow.action_start_time = time.time()
        self.client.tell('break', BREAK_AFTER_STEP)

    @qtsig('')
    def on_actionBreak2_triggered(self):
        self.on_actionBreak_triggered()

    @qtsig('')
    def on_actionBreakCount_triggered(self):
        self.mainwindow.action_start_time = time.time()
        self.client.tell('break', BREAK_NOW)

    @qtsig('')
    def on_actionContinue_triggered(self):
        self.mainwindow.action_start_time = time.time()
        self.client.tell('continue')

    @qtsig('')
    def on_actionStop_triggered(self):
        self.mainwindow.action_start_time = time.time()
        self.client.tell('stop', BREAK_NOW)

    @qtsig('')
    def on_actionStop2_triggered(self):
        self.on_actionStop_triggered()

    @qtsig('')
    def on_actionFinish_triggered(self):
        self.mainwindow.action_start_time = time.time()
        self.client.tell('stop', BREAK_AFTER_LINE)

    @qtsig('')
    def on_actionEmergencyStop_triggered(self):
        self.mainwindow.action_start_time = time.time()
        self.client.tell('emergency')

    @qtsig('')
    def on_clearQueue_clicked(self):
        if self.client.tell('unqueue', '*'):
            self.script_queue.clear()

    @qtsig('')
    def on_deleteQueueItem_clicked(self):
        item = self.queueView.currentItem()
        if not item:
            return
        reqno = item.data(Qt.UserRole)
        if self.client.tell('unqueue', str(reqno[0])):
            self.script_queue.remove(reqno[0])
