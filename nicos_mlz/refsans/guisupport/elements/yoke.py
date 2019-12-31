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
"""Classes to display the REFSANS instrument."""

from __future__ import absolute_import, division, print_function

from nicos.guisupport.qt import QColor, QGraphicsPathItem, QPainterPath, \
    QPen, QPointF, QPolygonF


class Yoke(QGraphicsPathItem):

    def __init__(self, parent=None, scene=None):
        QGraphicsPathItem.__init__(self, parent)
        self.setPath(self.shape())
        if not parent and scene:
            scene.addItem(self)
        self.setPen(QPen(QColor('red')))

    def shape(self):
        path = QPainterPath()
        x0, x1, h = 20, 15, 150
        path.addPolygon(QPolygonF([QPointF(-x0, 0), QPointF(x0, 0),
                                   QPointF(x1, -h), QPointF(-x1, -h)]))
        path.closeSubpath()
        return path
