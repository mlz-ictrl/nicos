# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Kenan Muric <kenan.muric@ess.eu>
#
# *****************************************************************************

from nicos.clients.gui.widgets.lineedit import CommandLineEdit as \
    CommandLineEditBase
from .utils import State, StyleSelector, refresh_widget


class CommandLineEdit(CommandLineEditBase, StyleSelector):
    """
    This widget extends from CommandLineEdit in NICOS core and overrides all
    functions that are using widget palette dependent functions in the base
    class. Stylesheets is the preferred choice in NICOS ESS.
    """

    def setStatus(self, status):
        CommandLineEditBase.setStatus(self, status)
        self.state = State.BUSY if status != 'idle' \
            else State.DEFAULT
        refresh_widget(self)
