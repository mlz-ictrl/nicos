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
from nicos.guisupport.qt import QBrush, QColor, QGraphicsLineItem, \
    QGraphicsRectItem, QGraphicsScene, QGraphicsTextItem, QGraphicsView, \
    QPainter, QTransform

from nicos_mlz.refsans.guisupport import Detector, Tube, Yoke


class RefsansView(QGraphicsView):

    pivotdist = 20

    def __init__(self, parent=None):
        scene = QGraphicsScene()
        QGraphicsView.__init__(self, scene)
        self.setRenderHints(QPainter.Antialiasing)

        self._tube = Tube(scene=scene)
        self._tube.setRotation(1)
        self._yoke = Yoke(scene=scene)
        t1 = QTransform()
        t1.translate(500, 0)
        self._yoke.setTransform(t1)
        self._pivotline = QGraphicsLineItem(-200, 0, 700, 0)
        scene.addItem(self._pivotline)
        self._pivot = QGraphicsRectItem(0, 0, 6, 10)
        t2 = QTransform()
        t2.translate(-3, -10)
        self._pivot.setTransform(t2)
        self._pivot.setBrush(QBrush(QColor('#1F1F1F')))
        scene.addItem(self._pivot)
        for i in range(13):
            txt = '%d' % (i + 1)
            self.t = QGraphicsTextItem(txt)
            bw = self.t.boundingRect().size().width()
            chrwidth = bw / (len(txt) + 1)
            x = (i - 9) * self.pivotdist - chrwidth / 2 + bw / len(txt)
            self.t.setX(x)
            scene.addItem(self.t)
        self._det = Detector(parent=self._tube, scene=scene)

        self.values = {
            'tubeangle': -1.0,
            'pivot': 1,
            'detpos': 620,
        }
        self.targets = self.values.copy()
        self.status = {
            'tubeangle': status.OK,
            'pivot': status.OK,
            'detpos': status.OK,
        }

    def resizeEvent(self, rsevent):
        s = rsevent.size()
        w, h = s.width(), s.height()
        scale = min(w / self._pivotline.boundingRect().width(),
                    h / (self._yoke.boundingRect().height() + 10 +
                         self.t.boundingRect().y() +
                         self.t.boundingRect().height()))
        transform = self.transform()
        transform.reset()
        transform.scale(scale, scale)
        self.setTransform(transform)
        QGraphicsView.resizeEvent(self, rsevent)

    def update(self):
        self._tube.setRotation(-self.values['tubeangle'])
        p = (self.values['pivot'] - 9) * self.pivotdist
        self._pivot.setX(p)
        self._tube.setX(p)
        self._yoke.setX(p)
        # 1 / 20 is the scaling of the tube length
        self._det.setX(self.values['detpos'] / 20)
        QGraphicsView.update(self)
