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

from nicos.guisupport.qt import QColor, QGraphicsLineItem, QLineF, QPen


class Beam(QGraphicsLineItem):
    """Class representing the neutron beam."""

    def __init__(self, fromObj, toObj, parent=None, scene=None):
        self._start = fromObj
        self._end = toObj
        QGraphicsLineItem.__init__(self, parent)
        self.setPen(QPen(QColor('white'), 4))
        self._beam = QGraphicsLineItem(parent)
        self._beam.setPen(QPen(QColor('blue'), 1))
        if not parent and scene:
            scene.addItem(self)
            scene.addItem(self._beam)
        self.update()
        self.setZValue(50)
        self._beam.setZValue(51)

    def paint(self, painter, options, widget):
        self.setLine(QLineF(self._start.scenePos(), self._end.scenePos()))
        QGraphicsLineItem.paint(self, painter, options, widget)

    def setLine(self, line):
        self._beam.setLine(line)
        QGraphicsLineItem.setLine(self, line)

    def boundingRect(self):
        # This refreshes the bounding rect
        self.setLine(QLineF(self._start.scenePos(), self._end.scenePos()))
        return QGraphicsLineItem.boundingRect(self)
