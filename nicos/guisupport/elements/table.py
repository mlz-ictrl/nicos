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

from __future__ import absolute_import, division, print_function

from nicos.guisupport.qt import QBrush, QColor, QGraphicsEllipseItem, \
    QGraphicsItemGroup, QPoint, QPointF, QRectF, QSizeF


class TableBase(QGraphicsEllipseItem):
    """Base class to display the tables of a TAS instrument."""

    _color = None
    _halo = None

    def __init__(self, x, y, size=40, parent=None, scene=None):
        self._origin = QPoint(x, y)
        self._size = size
        self._radius = size / 2
        if not self._color:
            self._color = QColor('white')
        QGraphicsEllipseItem.__init__(self, QRectF(-QPoint(size, size),
                                      QSizeF(2 * size, 2 * size)), parent)
        if not parent and scene:
            scene.addItem(self)
        self.setPos(x, y)
        self.setBrush(QBrush(self._color))

    def setState(self, state):
        if self._halo:
            self._halo.setState(state)
        self.update()

    def setPos(self, x, y=None):
        point = x if isinstance(x, QPointF) else QPointF(x, y)
        QGraphicsItemGroup.setPos(self, point)
