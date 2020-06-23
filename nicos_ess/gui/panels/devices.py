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

"""NICOS GUI panel with a list of all devices."""

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.panels.devices import \
    DevicesPanel as DefaultDevicesPanel
from nicos.core.status import BUSY, DISABLED, ERROR, NOTREACHED, OK, UNKNOWN, \
    WARN
from nicos.guisupport.qt import QCheckBox, Qt

from nicos_ess.gui.panels import get_icon


class DevicesPanel(DefaultDevicesPanel):
    panelName = 'ESS Devices'

    @property
    def groupIcon(self):
        return get_icon('group_work-24px.svg')

    @classmethod
    def _createIcons(cls):
        # hack to make non-Qt usage as in checksetups work
        if not hasattr(cls, 'statusIcon'):
            cls.statusIcon = {
                OK: get_icon('check_circle_green-24px.svg'),
                WARN: get_icon('warning_orange-24px.svg'),
                BUSY: get_icon('sync_orange-24px.svg'),
                NOTREACHED: get_icon('error-24px.svg'),
                DISABLED: get_icon('not_interested-24px.svg'),
                ERROR: get_icon('error-24px.svg'),
                UNKNOWN: get_icon('device_unknown-24px.svg'),
            }

    def __init__(self, parent, client, options):
        self._createIcons()
        DefaultDevicesPanel.__init__(self, parent, client, options)
        self.titleLbl.setText('Devices')

        self.errorOnly = QCheckBox('show only the errors', self)
        print(self.errorOnly.styleSheet())
        self.errorOnly.setStyleSheet('QCheckBox { '
                                     'background: #f5e042;'
                                     'border-radius: 5px'
                                     '}'
                                     )

        self.errorOnly.setAutoFillBackground(True)
        self.outViewLayout.insertWidget(2, self.errorOnly)

        self.errorOnly.stateChanged.connect(self.filterErrorOnly)
        client.status.connect(self.on_client_status)

    def _hide_top_level(self):
        for itemid in range(self.tree.topLevelItemCount()):
            topitem = self.tree.topLevelItem(itemid)
            hide = all([topitem.child(devid).isHidden() for devid in range(
                topitem.childCount())])
            if hide:
                topitem.setHidden(True)

    def _show_top_level(self):
        for itemid in range(self.tree.topLevelItemCount()):
            self.tree.topLevelItem(itemid).setHidden(False)

    def filterErrorOnly(self, state):
        if state == Qt.Checked:
            self._show_only_error_devices()
        else:
            self._show_all_devices()

    def _show_only_error_devices(self):
        for key, dev in self._devitems.items():
            if self._devinfo[key].status[0] == OK:
                dev.setHidden(True)
            else:
                dev.setHidden(False)
        self._hide_top_level()

    def _show_all_devices(self):
        for _, dev in self._devitems.items():
            if dev.isHidden():
                dev.setHidden(False)
        self._show_top_level()

    def on_client_status(self, status):
        if self.errorOnly.isChecked():
            self._show_all_devices()
            self._show_only_error_devices()
