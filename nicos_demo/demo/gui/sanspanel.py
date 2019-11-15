#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

"""Demonstrates a custom panel to do simple measurements with GUI."""

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import dialogFromUi, loadUi
from nicos.guisupport.qt import QColor, QDialogButtonBox, QIcon, QPushButton, \
    QSizePolicy, QStatusBar, QStyle, Qt, pyqtSlot
from nicos.guisupport.utils import setBackgroundColor
from nicos.protocols.cache import cache_load
from nicos.utils import findResource


class SANSPanel(Panel):
    panelName = 'SANS acquisition demo'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_demo/demo/gui/sanspanel.ui'))

        self.current_status = None

        self._idle = QColor('#99FF99')
        self._busy = QColor(Qt.yellow)

        self.statusBar = QStatusBar(self)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        client.cache.connect(self.on_client_cache)

        run = self.buttonBox.button(QDialogButtonBox.Yes)
        run.setText('Run')
        run.setIcon(QIcon(':/continue'))
        self.buttonBox.accepted.connect(self.on_start_clicked)

    def saveSettings(self, settings):
        settings.setValue('geometry', self.saveGeometry())

    def updateStatus(self, status, exception=False):
        self.current_status = status
        setBackgroundColor(self.curstatus,
                           self._idle if status == 'idle' else self._busy)

    def on_client_cache(self, data):
        _time, key, _op, value = data
        if key == 'exp/action':
            self.curstatus.setText(cache_load(value) or 'Idle')

    @pyqtSlot()
    def on_start_clicked(self):
        dpos = []
        for dp, cb in zip([1, 2, 5, 10, 20],
                          [self.dp1m, self.dp2m, self.dp5m, self.dp10m,
                           self.dp20m]):
            if cb.isChecked():
                dpos.append(dp)
        if not dpos:
            self.showInfo('Select at least one detector position!')
            return
        ctime = self.ctime.value()
        coll = self.coll10.isChecked() and '10m' or \
            (self.coll15.isChecked() and '15m' or '20m')
        code = 'maw(coll, %r)\nscan(det1_z, [%s], det, t=%.1f)\n' % \
            (coll, ', '.join(str(x) for x in dpos), ctime)
        self.execScript(code)

    def execScript(self, script):
        action = 'queue'
        if self.current_status != 'idle':
            qwindow = dialogFromUi(self, 'panels/question.ui')
            qwindow.questionText.setText('A script is currently running.  What'
                                         ' do you want to do?')
            icon = qwindow.style().standardIcon
            qwindow.iconLabel.setPixmap(
                icon(QStyle.SP_MessageBoxQuestion).pixmap(32, 32))
            b0 = QPushButton(icon(QStyle.SP_DialogCancelButton), 'Cancel')
            b1 = QPushButton(icon(QStyle.SP_DialogOkButton), 'Queue script')
            b2 = QPushButton(icon(QStyle.SP_MessageBoxWarning), 'Execute now!')
            qwindow.buttonBox.addButton(b0, QDialogButtonBox.ApplyRole)
            qwindow.buttonBox.addButton(b1, QDialogButtonBox.ApplyRole)
            qwindow.buttonBox.addButton(b2, QDialogButtonBox.ApplyRole)
            qwindow.buttonBox.setFocus()
            result = [0]

            def pushed(btn):
                if btn is b1:
                    result[0] = 1
                elif btn is b2:
                    result[0] = 2
                qwindow.accept()
            qwindow.buttonBox.clicked.connect(pushed)
            qwindow.exec_()
            if result[0] == 0:
                return
            elif result[0] == 2:
                action = 'execute'
        if action == 'queue':
            self.client.run(script)
        else:
            self.client.tell('exec', script)
