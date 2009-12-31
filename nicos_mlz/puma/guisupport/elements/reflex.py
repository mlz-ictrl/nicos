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
"""Classes to display the TAS instruments."""

import math

from nicos.guisupport.elements import TableBase
from nicos.guisupport.qt import QGraphicsEllipseItem

show = 1


class Reflex(TableBase):
    """Class displays a 'reflex'."""

    number = 0

    def __init__(self, radius, crystal, sample, detector, parent=None,
                 scene=None):
        self._number = Reflex.number + 1
        Reflex.number += 1
        self._crystal = crystal
        self._sample = sample
        self._detector = detector
        TableBase.__init__(self, 0, 0, 3, parent, scene)
        self._set_radius(radius)

    def _calculate_reflection(self):
        x1, y1 = self._crystal.scenePos().x(), self._crystal.scenePos().y()
        x2, y2 = self._detector.scenePos().x(), self._detector.scenePos().y()
        inangle = math.degrees(math.atan(
            (self._crystal.scenePos().y() - self._sample.scenePos().y()) /
            abs(self._sample.scenePos().x() - self._crystal.scenePos().x())))
        outangle = inangle + 2 * self._crystal.rotation()
        if self._number == show:
            print('calc reflection: x1, y1, x2, y2, rot: %f, %f, %f %f %f' % (
                x1, y1, x2, y2, self._detector.rotation()))
        # m = (x2 - x1) / (y2 - y1)
        m = math.tan(math.radians(outangle))
        r = self._radius
        if self._number == show:
            print('%f %f %f m: %f, r: %f' % (inangle, self._crystal.rotation(),
                                             outangle, m, r))
        m2_1 = (1 + m * m)
        t = m * (x1 - x2) + y2 - y1
        sq = math.sqrt(m2_1 * r * r - t * t)
        x = (x1 + m * m * x2 + m * (y1 - y2) - sq) / m2_1
        y = (m * m * y1 + y2 - m * (x2 - x1 + sq)) / m2_1
        r1 = math.sqrt(x * x + y * y)
        if self._number == show:
            print(self._crystal.pos(), self._crystal.scenePos())
            print('x, y: %f, %f %f' % (x, y, r1))
            print()
        return outangle, r1

    def _set_radius(self, radius):
        self._radius = radius
        self.setPos(-radius, -self._size)
        self.setTransformOriginPoint(radius, 0)

    def update(self):
        outangle, r1 = self._calculate_reflection()
        # print(outangle, r1)
        tp = self.transformOriginPoint()
        tp.setX(r1)
        self.setTransformOriginPoint(tp)
        # print(self.rotation())
        self.setRotation(outangle)
        # print(self._crystal.x(), self.rotation())
        QGraphicsEllipseItem.update(self)
