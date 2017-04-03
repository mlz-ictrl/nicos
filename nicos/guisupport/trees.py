#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""Tree widget for displaying devices/params.
"""

from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem

from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.pycompat import iteritems


class DeviceParamTree(NicosWidget, QTreeWidget):

    designer_description = 'Displays devices and their parameters'

    properties = {
        'showparams': PropDef(bool, True, 'Show parameters as subitems'),
    }

    def __init__(self, parent, designMode=False, **kwds):
        QTreeWidget.__init__(self, parent, **kwds)
        NicosWidget.__init__(self)
        self.only_explicit = True
        self.device_clause = None
        self.param_predicate = lambda name, value, info: True
        self.item_callback = lambda item, parent=None: True
        self.itemExpanded.connect(self.on_itemExpanded)

    def setClient(self, client):
        NicosWidget.setClient(self, client)
        self.client = client
        self._reinit()

    def on_client_connected(self):
        self._reinit()

    def on_client_device(self, data):
        self._reinit()

    def registerKeys(self):
        pass

    def on_itemExpanded(self, item):
        if item.childCount():
            return
        devname = item.text(0)
        if self.props['showparams']:
            paraminfo = self.client.getDeviceParamInfo(devname)
            for param, value in sorted(iteritems(
                    self.client.getDeviceParams(devname))):
                if not self.param_predicate(param, value,
                                            paraminfo.get(param)):
                    continue
                subitem = QTreeWidgetItem([param])
                if not self.item_callback(subitem, item):
                    continue
                item.addChild(subitem)

    def _reinit(self):
        self.clear()
        for devname in self.client.getDeviceList(
                only_explicit=self.only_explicit,
                special_clause=self.device_clause):
            item = QTreeWidgetItem([devname])
            # allow expanding interactively, even if we haven't populated
            # the parameter children yet
            item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
            if not self.item_callback(item):
                continue
            self.addTopLevelItem(item)
