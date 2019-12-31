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

from nicos.core import status
from nicos.guisupport.elements import statuscolor
from nicos.guisupport.qt import QBrush, QColor, QGraphicsRectItem, QPen, \
    QRectF, QSizeF, QTransform


class DetectorHalo(QGraphicsRectItem):

    def __init__(self, width, parent=None, scene=None):
        w = width + 2
        if parent and isinstance(parent, QGraphicsRectItem):
            rect = parent.rect()
            size = rect.size()
            size += QSizeF(w, w)
            rect.setSize(size)
        else:
            rect = QRectF()
        QGraphicsRectItem.__init__(self, rect, parent)
        transform = QTransform()
        transform.translate(-w / 2, -w / 2)
        self.setTransform(transform)
        self.setBrush(QBrush(statuscolor[status.OK]))
        self.setPen(QPen(statuscolor[status.OK], width))

    def setState(self, state):
        pen = self.pen()
        pen.setColor(statuscolor[state])
        self.setPen(pen)
        self.update()


class Detector(QGraphicsRectItem):

    def __init__(self, parent=None, scene=None):
        QGraphicsRectItem.__init__(self, 0, 0, 10, 45, parent)
        transform = QTransform()
        transform.translate(0, 5)
        self.setTransform(transform)
        self.setBrush(QBrush(QColor('#00FF00')))
        if not parent and scene:
            scene.addItem(self)
        self._halo = DetectorHalo(5, self, scene)

    def setState(self, state):
        self._halo.setState(state)
        self.update()
