#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI panel for generic panels made with Qt designer."""

from __future__ import with_statement

__version__ = "$Revision$"

from PyQt4.QtCore import SIGNAL

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.protocols.cache import OP_TELLOLD, cache_load
from nicos.guisupport.widget import DisplayWidget, InteractiveWidget


class GenericPanel(Panel):
    panelName = 'Generic'  # XXX this is not unique

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        self.connect(client, SIGNAL('cache'), self.on_client_cache)
        self.connect(client, SIGNAL('connected'), self.on_client_connected)
        self._reg_keys = {}

    def setOptions(self, options):
        # XXX standard dir?
        loadUi(self, options['uifile'], options.get('dir', ''))

        for ch in self.findChildren(DisplayWidget):
            if isinstance(ch, InteractiveWidget):
                ch.setClient(self.client)
            ch.setSource(self)

        if self.client.connected:
            # get initial values of display widgets
            self.on_client_connected()

    def register(self, widget, key):
        key = key.lower().replace('.', '/')
        self._reg_keys.setdefault(key, []).append(widget)
        return key

    def on_client_connected(self):
        # request initial value for all keys we have registered
        values = self.client.ask('getcachekeys', ','.join(self._reg_keys))
        for key, value in values:
            for widget in self._reg_keys[key]:
                widget.on_keyChange(key, value, 0, False)

    def on_client_cache(self, (time, key, op, value)):
        if key in self._reg_keys:
            cvalue = cache_load(value)
            for widget in self._reg_keys[key]:
                widget.on_keyChange(key, cvalue, time,
                                    value is None or op == OP_TELLOLD)
