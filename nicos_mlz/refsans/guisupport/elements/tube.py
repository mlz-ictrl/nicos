#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

from nicos.core import status
from nicos.guisupport.elements import statuscolor
from nicos.guisupport.qt import QBrush, QGraphicsPathItem, QPainterPath, \
    QPen, QPointF, QRectF, QTransform


class Tube(QGraphicsPathItem):

    _halo = None

    def __init__(self, parent=None, scene=None):
        QGraphicsPathItem.__init__(self, parent)
        self.setPath(self.shape())
        transform = QTransform()
        transform.translate(0, -60)
        self.setTransform(transform)
        self.setTransformOriginPoint(QPointF(0, 50))
        if not parent and scene:
            scene.addItem(self)
        self._halo = TubeHalo(10, self, scene)
        self.setState(status.OK)

    def setState(self, state):
        if self._halo:
            self._halo.setState(state)
        self.update()

    def shape(self):
        path = QPainterPath()
        path.addRect(QRectF(0, 0, 600, 50))
        rect = QRectF(0, 0, 10, 10)
        rect.translate(-10, 20)
        path.addRect(rect)
        return path

    def boundingRect(self):
        r = QGraphicsPathItem.boundingRect(self)
        if self._halo:
            r = r.united(self._halo.boundingRect())
        # this scaling has to be done due the rotation of the tube
        # TODO: find a better solution
        r.setSize(r.size() * 1.1)
        return r


class TubeHalo(QGraphicsPathItem):

    def __init__(self, width=10, parent=None, scene=None):
        QGraphicsPathItem.__init__(self, parent)
        self._width = width
        self.setPath(self.shape())
        if not parent and scene:
            scene.addItem(self)
        self.setBrush(QBrush(statuscolor[status.OK]))
        self.setPen(QPen(statuscolor[status.OK], width))

    def shape(self):
        path = QPainterPath()
        w = self._width + 2
        r = QRectF(0, 0, 600 + w, 50 + w)
        r.translate(-w / 2, -w / 2)
        path.addRect(r)
        return path

    def setState(self, state):
        pen = self.pen()
        pen.setColor(statuscolor[state])
        self.setPen(pen)
        self.update()
