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

from enum import Enum
from nicos.guisupport.qt import pyqtProperty


class State(Enum):
    DEFAULT, BUSY = range(2)


class StyleSelector:
    """
    A class that encapsulates the state used for stylesheet selection
    in the relevant qss files.
    """

    def __init__(self):
        self.state = State.DEFAULT

    @pyqtProperty(str)
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = str(value).split(".")[-1]


def refresh_widget(widget):
    """
    Function that correctly updates the widget with a new stylesheet.
    """
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()
