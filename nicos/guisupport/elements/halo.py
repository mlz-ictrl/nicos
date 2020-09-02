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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""Classes to display the TAS instruments."""

from nicos.core import status
from nicos.guisupport.elements.colors import statuscolor
from nicos.guisupport.qt import QBrush, QGraphicsEllipseItem, QPen, QPoint, \
    QRectF, QSizeF


class Halo(QGraphicsEllipseItem):
    """Base class to display the halos of the tables."""

    def __init__(self, x, y, size=60, width=10, parent=None, scene=None):
        self._width = width
        s = size + width / 2
        QGraphicsEllipseItem.__init__(self, QRectF(-QPoint(s, s),
                                      QSizeF(2 * s, 2 * s)), parent)
        self.setBrush(QBrush(statuscolor[status.OK]))
        if not parent and scene:
            scene.addItem(self)
        self.setPos(x, y)
        self.setState(status.OK)

    def setState(self, state):
        self.setPen(QPen(statuscolor[state], self._width))
        self.update()
