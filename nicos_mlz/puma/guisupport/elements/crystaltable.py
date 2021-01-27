#  -*- coding: utf-8 -*-
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""Classes to display the PUMA multi analyzer devices."""

from nicos.guisupport.elements import Crystal
from nicos.guisupport.elements.halo import Halo
from nicos.guisupport.qt import QPointF


class CrystalTable(Crystal):
    """Class to display the multi detector crystal table including crystal."""

    _halowidth = 6

    def __init__(self, x, y, size=40, parent=None, scene=None):
        Crystal.__init__(self, x, y, size, parent, scene)
        self._halo = Halo(0, 0, size, self._halowidth, self, scene)
        self._halo.setZValue(-10)

    def setPos(self, x, y=None):
        point = x if isinstance(x, QPointF) else QPointF(x, y)
        Crystal.setPos(self, point)

    def rect(self):
        return self._halo.rect()
