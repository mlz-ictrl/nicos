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

"""Dialog for entering authentication data."""

from PyQt4.QtGui import QDialog, QFontMetrics, QIcon, QListWidgetItem, QPalette
from PyQt4.QtCore import QSize


try:
    from PyQt4.QtCore import QPyNullVariant  # pylint: disable=E0611
except ImportError:
    class QPyNullVariant(object):
        pass

from nicos.protocols.daemon import DEFAULT_PORT
from nicos.clients.base import ConnectionData
from nicos.clients.gui.utils import loadUi


class ConnectionDialog(QDialog):
    """A dialog to request connection parameters."""

    @classmethod
    def getConnectionData(cls, parent, connpresets, lastpreset, lastdata):
        self = cls(parent, connpresets, lastpreset, lastdata)
        ret = self.exec_()
        if ret != QDialog.Accepted:
            return None, None, None
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
        if not new_name:
            preset_name = self.newPresetName.text()
        return new_name, new_data, preset_name

    def __init__(self, parent, connpresets, lastpreset, lastdata):
        QDialog.__init__(self, parent)
        loadUi(self, 'auth.ui', 'dialogs')
        self.connpresets = connpresets
        if isinstance(lastpreset, QPyNullVariant):
            lastpreset = None

        pal = self.quickList.palette()
        pal.setColor(QPalette.Window, pal.color(QPalette.Base))
        self.quickList.setPalette(pal)

        if len(connpresets) < 3:
            self.quickList.hide()
        else:
            self.quickList.setStyleSheet('padding: 10px 5px;')
            self.quickList.clear()
            maxw = 64
            icon = QIcon(':/appicon')
            metric = QFontMetrics(self.quickList.font())
            for preset in sorted(connpresets):
                item = QListWidgetItem(preset, self.quickList)
                item.setIcon(icon)
                maxw = max(maxw, metric.width(preset))
            self.quickList.setGridSize(QSize(maxw + 8, 72))
            # the automatic sizing still leads to a vertical scrollbar
            hint = self.quickList.sizeHint()
            hint.setHeight(hint.height() + 50)
            hint.setWidth(max(4.7 * maxw, 330))
            self.quickList.setMinimumSize(hint)
            self.resize(self.sizeHint())

        self.presetOrAddr.addItems(sorted(connpresets))
        self.presetOrAddr.setEditText(lastpreset)
        if not lastpreset:
            # if we have no stored last preset connection, put in the raw data
            self.presetOrAddr.setEditText(
                '%s:%s' % (lastdata.host, lastdata.port))
        self.userName.setText(lastdata.user)
        self.password.setFocus()
        self.presetFrame.hide()
        self.resize(QSize(self.width(), self.minimumSize().height()))

    def on_presetOrAddr_editTextChanged(self, text):
        if text in self.connpresets:
            conn = self.connpresets[text]
            self.userName.setText(conn.user)
            self.viewonly.setChecked(conn.viewonly)
            self.presetFrame.hide()
        else:
            self.presetFrame.show()

    def on_quickList_itemClicked(self, item):
        conn = self.connpresets[item.text()]
        self.presetOrAddr.setEditText(item.text())
        self.userName.setText(conn.user)
        self.viewonly.setChecked(conn.viewonly)
        self.password.setFocus()

    def on_quickList_itemDoubleClicked(self, item):
        conn = self.connpresets[item.text()]
        if conn.user == 'guest':
            self.password.setText('')
            self.accept()
