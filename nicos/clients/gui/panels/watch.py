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

"""NICOS GUI watch variable panel component."""

from PyQt4.QtGui import QInputDialog, QMessageBox, QTreeWidgetItem
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import pyqtSignature as qtsig

from nicos.clients.gui.utils import loadUi, setBackgroundColor
from nicos.clients.gui.panels import Panel
from nicos.pycompat import iteritems


class WatchPanel(Panel):
    panelName = 'Watch'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'watch.ui', 'panels')

        self.watch_items = {}
        self.connect(client, SIGNAL('watch'), self.on_client_watch)
        self.connect(client, SIGNAL('initstatus'), self.on_client_initstatus)

    def setCustomStyle(self, font, back):
        self.watchView.setFont(font)
        setBackgroundColor(self.watchView, back)

    def updateStatus(self, status, exception=False):
        isconnected = status != 'disconnected'
        self.addWatch.setEnabled(isconnected)
        self.deleteWatch.setEnabled(isconnected)
        self.oneShotEval.setEnabled(isconnected)

    def on_client_initstatus(self, state):
        self.on_client_watch(state['watch'])

    def on_client_watch(self, data):
        values = data
        names = set()
        for name, val in iteritems(values):
            name = name[:name.find(':')]
            if name in self.watch_items:
                self.watch_items[name].setText(1, str(val))
            else:
                newitem = QTreeWidgetItem(self.watchView,
                                          [str(name), str(val)])
                self.watchView.addTopLevelItem(newitem)
                self.watch_items[name] = newitem
            names.add(name)
        removed = set(self.watch_items) - names
        for itemname in removed:
            self.watchView.takeTopLevelItem(
                self.watchView.indexOfTopLevelItem(
                    self.watch_items[itemname]))
            del self.watch_items[itemname]

    @qtsig('')
    def on_addWatch_clicked(self):
        expr, ok = QInputDialog.getText(self, 'Add watch expression',
                                        'New expression to watch:')
        if not ok:
            return
        newexpr = [expr + ':default']
        self.client.tell('watch', newexpr)

    @qtsig('')
    def on_deleteWatch_clicked(self):
        item = self.watchView.currentItem()
        if not item:
            return
        expr = item.text(0)
        delexpr = [expr + ':default']
        self.client.tell('unwatch', delexpr)

    @qtsig('')
    def on_oneShotEval_clicked(self):
        expr, ok = QInputDialog.getText(self, 'Evaluate an expression',
                                        'Expression to evaluate:')
        if not ok:
            return
        ret = self.client.eval(expr, stringify=True)
        QMessageBox.information(self, 'Result', ret)
