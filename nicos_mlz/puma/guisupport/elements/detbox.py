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
"""Classes to display the PUMA Multi analyzer."""

from __future__ import absolute_import, division, print_function

from nicos.guisupport.qt import QGraphicsPathItem, QLineF, QPainter, \
    QPainterPath, QPointF, QPolygonF, QRectF, Qt


class DetectorBox(QGraphicsPathItem):

    def __init__(self, r=762, span=48, parent=None):
        self.radius1 = r - 329
        self.radius2 = r + 58
        self.circle1 = QRectF(-self.radius1, -self.radius1, 2 * self.radius1,
                              2 * self.radius1)
        self.circle2 = QRectF(-self.radius2, -self.radius2, 2 * self.radius2,
                              2 * self.radius2)
        self.startAngle = 180 - span
        self.spanAngle = span
        w = 10
        self.boundingRectTemp = self.circle1.adjusted(-w, -w, w, w)
        QGraphicsPathItem.__init__(self, parent=parent)

    def paint(self, painter, options, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.shape())

    def shape(self):
        aoffs = 5  # additional angle for the inner arc
        path = QPainterPath()

        # draw inner circle of the detector box
        path.arcMoveTo(self.circle1, self.startAngle - aoffs)
        path.arcTo(self.circle1, self.startAngle - aoffs,
                   self.spanAngle + 2 * aoffs)

        # draw outer circle of the detector box
        path.arcMoveTo(self.circle2, self.startAngle)
        path.arcTo(self.circle2, self.startAngle, self.spanAngle)

        # calculate left inner point of the box
        tmpLine = QLineF(QPointF(0, 0), QPointF(-self.radius1, 0))
        tmpLine.setAngle(tmpLine.angle() + aoffs)

        # draw left line
        path.addPolygon(QPolygonF([tmpLine.p2(),
                                   QPointF(-self.radius2, 0)]))

        # calculate right inner point of the box
        tmpLine = QLineF(QPointF(0, 0), QPointF(-self.radius1, 0))
        tmpLine.setAngle(self.startAngle - aoffs)

        # calculate right outer point of the box
        line2 = QLineF(QPointF(0, 0), QPointF(-self.radius2, 0))
        line2.setAngle(self.startAngle)

        # draw right line of the box
        path.addPolygon(QPolygonF([tmpLine.p2(), line2.p2()]))
        return path
