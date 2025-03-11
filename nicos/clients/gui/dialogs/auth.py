# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""Dialog for entering authentication data."""
from collections import OrderedDict
from os import path

from nicos.clients.base import ConnectionData
from nicos.clients.gui.utils import loadUi, splitTunnelString
from nicos.guisupport.qt import QDialog, QFontMetrics, QIcon, \
    QListWidgetItem, QPalette, QPixmap, QSize, pyqtSlot
from nicos.protocols.daemon.classic import DEFAULT_PORT


class ConnectionDialog(QDialog):
    """A dialog to request connection parameters."""

    ui = path.join('dialogs', 'auth.ui')

    @classmethod
    def getConnectionData(cls, parent, connpresets, lastpreset, lastdata,
                          tunnel=''):
        self = cls(parent, connpresets, lastpreset, lastdata, tunnel)
        ret = self.exec()
        if ret != QDialog.DialogCode.Accepted:
            return None, None, None, tunnel
        new_addr = self.presetOrAddr.currentText()
        new_name = preset_name = ''
        if new_addr in connpresets:
            new_data = connpresets[new_addr].copy()
            new_name = new_addr
            if self.userName.text():
                new_data.user = self.userName.text()
            new_data.password = self.password.text()
        else:
            try:
                host, port = new_addr.split(':')
                port = int(port)
            except ValueError:
                host = new_addr
                port = DEFAULT_PORT
            new_data = ConnectionData(host, port, self.userName.text(),
                                      self.password.text())
        new_data.viewonly = self.viewonly.isChecked()
        new_data.expertmode = self.expertmode.isChecked()
        if tunnel:
            tunnel = '%s:%s@%s' % (self.remoteUserName.text(),
                                   self.remotePassword.text(),
                                   self.remoteHost.text())
        else:
            tunnel = ''
        if not new_name:
            preset_name = self.newPresetName.text()
        return new_name, new_data, preset_name, tunnel

    def __init__(self, parent, connpresets, lastpreset, lastdata, tunnel=''):
        QDialog.__init__(self, parent)
        loadUi(self, self.ui)
        if hasattr(parent, 'facility_logo') and parent.facility_logo:
            self.logoLabel.setPixmap(QPixmap(parent.facility_logo))
        self.connpresets = OrderedDict(sorted(connpresets.items()))

        pal = self.quickList.palette()
        pal.setColor(QPalette.ColorRole.Window,
                     pal.color(QPalette.ColorRole.Base))
        self.quickList.setPalette(pal)

        if len(self.connpresets) < 3:
            self.quickList.hide()
        else:
            self.quickList.setStyleSheet('padding: 10px 5px;')
            self.quickList.clear()
            maxw = 64
            icon = QIcon(':/appicon')
            metric = QFontMetrics(self.quickList.font())
            for preset in self.connpresets:
                item = QListWidgetItem(preset, self.quickList)
                item.setIcon(icon)
                maxw = max(maxw, metric.horizontalAdvance(preset))
            self.quickList.setGridSize(QSize(maxw + 8, 72))
            # the automatic sizing still leads to a vertical scrollbar
            hint = self.quickList.sizeHint()
            hint.setHeight(hint.height() + 50)
            hint.setWidth(round(max(4.7 * maxw, 330)))
            self.quickList.setMinimumSize(hint)
            self.resize(self.sizeHint())

        self.presetOrAddr.addItems(self.connpresets)
        if lastdata:
            self.presetOrAddr.setEditText(
                '%s:%s' % (lastdata.host, lastdata.port))
            self.viewonly.setChecked(lastdata.viewonly)
            self.expertmode.setChecked(lastdata.expertmode)
            self.userName.setText(lastdata.user)
        if lastpreset and lastpreset in self.connpresets:  # prefer preset name
            index = list(self.connpresets).index(lastpreset)
            self.presetOrAddr.setCurrentIndex(index)
        self.password.setFocus()

        self.viaFrame.setHidden(not tunnel)
        if tunnel:
            host, username, password = splitTunnelString(tunnel)
            self.remotePassword.setText(password)
            if not password:
                self.remotePassword.setFocus()
            self.remoteUserName.setText(username)
            if not username:
                self.remoteUserName.setFocus()
            self.remoteHost.setText(host)
            if not host:
                self.remoteHost.setFocus()

        self.presetLabel.hide()
        self.newPresetName.hide()
        self.resize(QSize(self.width(), self.minimumSize().height()))

    @pyqtSlot(int)
    def on_presetOrAddr_currentIndexChanged(self, _idx):
        text = self.presetOrAddr.currentText()
        if text in self.connpresets:
            conn = self.connpresets[text]
            self.userName.setText(conn.user)
            self.viewonly.setChecked(conn.viewonly)
            self.expertmode.setChecked(conn.expertmode)
            self.presetLabel.hide()
            self.newPresetName.hide()
        else:
            self.presetLabel.show()
            self.newPresetName.show()

    def on_presetOrAddr_editTextChanged(self, text):
        # If the text is not the currently selected preset,
        # we are typing a host name and should have the possibility
        # to save as a preset.
        index = self.presetOrAddr.currentIndex()
        if text != self.presetOrAddr.itemText(index):
            self.presetLabel.show()
            self.newPresetName.show()

    def on_quickList_itemClicked(self, item):
        self.presetOrAddr.setCurrentIndex(
            self.presetOrAddr.findText(item.text()))
        self.password.setFocus()

    def on_quickList_itemDoubleClicked(self, item):
        conn = self.connpresets[item.text()]
        if conn.user == 'guest':
            self.password.setText('')
            self.accept()
