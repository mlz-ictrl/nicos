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

from math import radians, sin

from nicos.core import status
from nicos.guisupport.elements import Beam, Sample, TableTarget
from nicos.guisupport.qt import QColor, QGraphicsEllipseItem, QGraphicsItem, \
    QGraphicsScene, QGraphicsView, QLineF, QPainter, QPainterPath, QPointF, \
    QRectF, Qt

from nicos_mlz.puma.guisupport.elements import CrystalTable, DetectorBox, \
    DetectorGuide, DetectorTable


class ArcGraphicsItem(QGraphicsItem):

    def __init__(self, x, y, r, start, span, parent=None):
        self.circle = QRectF(x - r, y - r, 2 * r, 2 * r)
        self.startAngle = start
        self.spanAngle = span
        w = 10
        self.boundingRectTemp = self.circle.adjusted(-w, -w, w, w)
        QGraphicsItem.__init__(self)
        self._color = QColor('blue')

    def boundingRect(self):
        # outer most edges
        return self.boundingRectTemp

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw arc
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.shape())

    def shape(self):
        path = QPainterPath()
        path.arcMoveTo(self.circle, self.startAngle)
        path.arcTo(self.circle, self.startAngle, self.spanAngle)
        return path


class ThreePointArcGraphicsItem(ArcGraphicsItem):

    def __init__(self, point1=QPointF(0, 0), point2=QPointF(0, 1),
                 point3=QPointF(1, 1)):
        lineBC = QLineF(point2, point3)
        lineAC = QLineF(point1, point3)
        lineBA = QLineF(point2, point1)

        rad = abs(lineBC.length() / (2 * sin(radians(lineAC.angleTo(lineBA)))))

        bisectorBC = QLineF(lineBC.pointAt(0.5), lineBC.p2())
        bisectorBC.setAngle(lineBC.normalVector().angle())

        bisectorBA = QLineF(lineBA.pointAt(0.5), lineBA.p2())
        bisectorBA.setAngle(lineBA.normalVector().angle())
        center = QPointF()
        bisectorBA.intersect(bisectorBC, center)

        self.circle = QRectF(center.x() - rad, center.y() - rad, 2 * rad,
                             2 * rad)

        lineOA = QLineF(center, point1)
        lineOB = QLineF(center, point2)
        lineOC = QLineF(center, point2)

        startAngle = lineOA.angle()
        spanAngle = lineOA.angleTo(lineOC)
        # Make sure that the span angle covers all three points with the second
        # point in the middle
        if abs(spanAngle) < abs(lineOA.angleTo(lineOB)) or \
           abs(spanAngle) < abs(lineOB.angleTo(lineOC)):
            # swap the end point and invert the spanAngle
            startAngle = lineOC.angle()
            spanAngle = 360 - self.spanAngle
        ArcGraphicsItem.__init__(self, center.x(), center.y(), rad, startAngle,
                                 spanAngle)


class MultiAnalyzerView(QGraphicsView):
    """Widget to visualise the current positions of the TAS."""

    num_crystals = 11
    detradius = 762  # detector radius

    _crystals = []
    _crystals_t = []
    _inbeams = []
    _outbeams = []
    _detectors = []
    _detectors_t = []
    _reflections = []
    _guides = []
    _sample = None

    detsize = 12
    crystalsize = 10
    detopen = 48

    def __init__(self):
        scene = QGraphicsScene()
        QGraphicsView.__init__(self, scene)
        self.setRenderHints(QPainter.Antialiasing)

        self._sample = Sample(0, 0, scene=scene)

        # draw the center point of the detector circle
        scene.addItem(QGraphicsEllipseItem(-2, -2, 4, 4))

        # draw the detector circle
        # scene.addItem(ArcGraphicsItem(0, 0, self.detradius + 10, 0, 180))

        # draw detector box
        self._detbox = DetectorBox(self.detradius, self.detopen)
        scene.addItem(self._detbox)

        # default values (used when no such devices are configured)
        self.values = {
            'rd1': 27.5,
            'rd2': 25.0,
            'rd3': 22.5,
            'rd4': 20.0,
            'rd5': 17.5,
            'rd6': 15.0,
            'rd7': 12.5,
            'rd8': 10.0,
            'rd9': 7.5,
            'rd10': 5.0,
            'rd11': 2.5,
            'rg1': 0.0,
            'rg2': 0.0,
            'rg3': 0.0,
            'rg4': 0.0,
            'rg5': 0.0,
            'rg6': 0.0,
            'rg7': 0.0,
            'rg8': 0.0,
            'rg9': 0.0,
            'rg10': 0.0,
            'rg11': 0.0,
            'ra1': 0.0,
            'ra2': 0.0,
            'ra3': 0.0,
            'ra4': 0.0,
            'ra5': 0.0,
            'ra6': 0.0,
            'ra7': 0.0,
            'ra8': 0.0,
            'ra9': 0.0,
            'ra10': 0.0,
            'ra11': 0.0,
            'ta1': 125.0,
            'ta2': 112.0,
            'ta3': 99.0,
            'ta4': 86.0,
            'ta5': 73.0,
            'ta6': 60.0,
            'ta7': 47.0,
            'ta8': 34.0,
            'ta9': 21.0,
            'ta10': 8.0,
            'ta11': -5.0,
            'cad': 0.0,
            'lsa': 910.,
        }
        self.targets = self.values.copy()
        self.status = {
            'rd1': status.OK,
            'rd2': status.OK,
            'rd3': status.OK,
            'rd4': status.OK,
            'rd5': status.OK,
            'rd6': status.OK,
            'rd7': status.OK,
            'rd8': status.OK,
            'rd9': status.OK,
            'rd10': status.OK,
            'rd11': status.OK,
            'rg1': status.OK,
            'rg2': status.OK,
            'rg3': status.OK,
            'rg4': status.OK,
            'rg5': status.OK,
            'rg6': status.OK,
            'rg7': status.OK,
            'rg8': status.OK,
            'rg9': status.OK,
            'rg10': status.OK,
            'rg11': status.OK,
            'ra1': status.OK,
            'ra2': status.OK,
            'ra3': status.OK,
            'ra4': status.OK,
            'ra5': status.OK,
            'ra6': status.OK,
            'ra7': status.OK,
            'ra8': status.OK,
            'ra9': status.OK,
            'ra10': status.OK,
            'ra11': status.OK,
            'ta1': status.OK,
            'ta2': status.OK,
            'ta3': status.OK,
            'ta4': status.OK,
            'ta5': status.OK,
            'ta6': status.OK,
            'ta7': status.OK,
            'ta8': status.OK,
            'ta9': status.OK,
            'ta10': status.OK,
            'ta11': status.OK,
            'cad': status.OK,
            'lsa': status.OK,
        }

        for i in range(self.num_crystals):
            dt = DetectorTable(self.detsize, self.detradius, scene=scene)
            self._detectors.append(dt)
            self._guides.append(DetectorGuide(dt))

            t = TableTarget(0, 0, self.detsize, scene=scene)
            # move the origin to make the rotation very easy
            t.setPos(-self.detradius, -self.detsize)
            t.setTransformOriginPoint(self.detradius, 0)
            self._detectors_t.append(t)

            y = (self.num_crystals // 2 - i) * 20
            self._crystals.append(CrystalTable(0, y, self.crystalsize,
                                               scene=scene))
            self._crystals_t.append(TableTarget(0, y, self.crystalsize,
                                                scene=scene))
            self._inbeams.append(Beam(self._sample, self._crystals[i],
                                      scene=scene))
            self._outbeams.append(Beam(self._crystals[i], self._detectors[i],
                                       scene=scene))
            # self._outbeams.append(
            #    Beam(self._crystals[i], self._reflections[i], scene=scene))
            # self._reflections.append(
            #     Reflex(r, self._crystals[i], self._sample,
            #            self._detectors[i], scene=scene))
        QGraphicsView.update(self)

    def resizeEvent(self, rsevent):
        s = rsevent.size()
        w, h = s.width(), s.height()
        scale = min(w / (self.detradius + 50 + self._sample.pos().x() +
                         self._sample.boundingRect().width()),
                    h / (self.detradius + 3 * 50 + self._crystals[0].pos().y() +
                         self._crystals[0].boundingRect().height()))
        transform = self.transform()
        transform.reset()
        transform.scale(scale, scale)
        self.setTransform(transform)
        QGraphicsView.resizeEvent(self, rsevent)

    def update(self):
        self._sample.setPos(self.values['lsa'], 0)
        cadrot = -self.values['cad']  # rotation has opposite sign
        self._detbox.setRotation(cadrot - 10)
        for i in range(self.num_crystals):
            self._detectors[i].setState(max(self.status['rd%d' % (i + 1)],
                                            self.status['rg%d' % (i + 1)]))
            self._detectors[i].setRotation(
                -(self.values['rd%d' % (i + 1)] - cadrot))
            self._detectors_t[i].setRotation(
                -(self.targets['rd%d' % (i + 1)] - cadrot))
            self._guides[i].setRotation(-self.values['rg%d' % (i + 1)])

            self._crystals[i].setState(max(self.status['ta%d' % (i + 1)],
                                           self.status['ra%d' % (i + 1)]))
            self._crystals[i].setRotation(-self.values['ra%d' % (i + 1)])
            self._crystals[i].setX(self.values['ta%d' % (i + 1)])
            self._crystals_t[i].setX(self.targets['ta%d' % (i + 1)])
        # for r in self._reflections:
        #     r.update()
        for l in self._inbeams + self._outbeams:
            l.update()
        QGraphicsView.update(self)
