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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

from nicos.clients.gui.panels.base import SetupDepPanelMixin
from nicos.guisupport.qt import QHBoxLayout, QLayout, QVBoxLayout, QWidget
from nicos.utils.loggers import NicosLogger


class Boxed(QWidget, SetupDepPanelMixin):
    setWidgetVisible = SetupDepPanelMixin.setWidgetVisible
    layout_type = QLayout
    logger_name = 'Boxed'

    def __init__(self, item, window, menuwindow, topwindow, parent=None):
        from nicos.clients.gui.panels.utils import createWindowItem
        QWidget.__init__(self, parent)
        self.log = NicosLogger(self.logger_name)
        self.log.parent = topwindow.log
        layout = self.layout_type(parent)
        SetupDepPanelMixin.__init__(self, window.client, item.options)
        for subitem in item.children:
            sub = createWindowItem(subitem, window, menuwindow, topwindow,
                                   self.log)
            if sub:
                layout.addWidget(sub)
        self.setLayout(layout)


class VerticalBoxed(Boxed):
    layout_type = QVBoxLayout
    logger_name = 'VerticalBoxed'


class HorizontalBoxed(Boxed):
    layout_type = QHBoxLayout
    logger_name = 'HorizontalBoxed'
